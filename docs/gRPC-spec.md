# Monitor Protocol — gRPC Contract (draft)

This defines the **protocol contract** between the launcher and the trainer-monitor. The monitor is a separate Rust binary in its own repo; this spec is what the launcher targets so both sides can be built independently. Transport follows the gRPC plan discussed in DeckCheatz/trainer-monitor, with room for a secondary payload (e.g. OMMXP) later.

## Transport

gRPC on `127.0.0.1`. Launcher picks a free port (possibly from a range), passes it via CLI arg. Fallback error file via `--error-file` (Z:-path) if the connection fails entirely.

```
monitor --port <PORT> --error-file Z:\path\to\error.json --timeout 10
```

Proto package: `wand.monitor.v1`. Major version bumps = new package (`v2`); additive changes stay in `v1` (protobuf is forward-compatible).

## Service Definition

```proto
syntax = "proto3";
package wand.monitor.v1;

service Monitor {
  // Handshake: launcher calls right after connecting.
  rpc Hello(HelloRequest) returns (HelloReply);

  // Session events, streamed for the whole session lifetime.
  // Subscribe before queueing anything.
  rpc Events(EventFilter) returns (stream Event);

  // Queue-then-execute model.
  rpc Execute(ProcessSpec) returns (QueuedAck);
  rpc Finished(Empty) returns (Empty);

  rpc Stop(StopRequest) returns (StoppedAck);
  rpc Restart(RestartRequest) returns (RestartAck);

  rpc Exit(ExitRequest) returns (Done);
  rpc Shutdown(Empty) returns (Done);

  // Keepalive (or use standard grpc.health.v1).
  rpc Ping(Empty) returns (Pong);
}
```

## Messages

```proto
message HelloRequest {
  string launcher_version = 1;
}

message HelloReply {
  string version = 1;        // semver of the protocol/monitor
}

message ProcessSpec {
  string name = 1;           // identifier, duplicate -> error
  string exe = 2;            // Z:-path, relative supported
  repeated string args = 3;
  string close_with = 4;     // close this process when named one exits
  float close_timeout = 5;   // sec before kill, default 2
  StreamMode stdout_mode = 6;
  StreamMode stderr_mode = 7;
}

enum StreamMode {
  CONSOLE = 0;   // default, Wine console
  EVENT = 1;     // routed to launcher via output events
  BOTH = 2;      // tee
}

message QueuedAck {
  string name = 1;
}

message StopRequest {
  string name = 1;
  float kill_timeout = 2;    // default 3; 0 = immediate; -1 = never kill
}

message StoppedAck {
  string name = 1;
}

message RestartRequest {
  float kill_timeout = 1;    // default 3
}

// Empty ack; fresh handshake follows as an event.

message ExitRequest {
  int32 code = 1;            // session exit code
}

message Done {
  Reason reason = 1;
  int32 code = 2;
}

enum Reason {
  FINISHED = 0;              // all exited normally
  ERRORED = 1;               // something went wrong, investigate
}
```

## Events

Streamed on the `Events` RPC. One message per occurrence.

```proto
message Event {
  oneof kind {
    Ready ready = 1;
    Started started = 2;
    Output output = 3;
    Exited exited = 4;
    Closed closed = 5;
    ErrorEvent error = 6;
    Idle idle = 7;
    Done done = 8;
  }
}

message Ready {
  string version = 1;
}

message Started {
  string name = 1;
  uint32 pid = 2;
}

message Output {
  string name = 1;
  StreamKind type = 2;       // STDOUT / STDERR
  uint32 lines = 3;          // usually 1
  string content = 4;
}

enum StreamKind {
  STDOUT = 0;
  STDERR = 1;
}

message Exited {
  string name = 1;
  int32 code = 2;
}

message Closed {
  string name = 1;
  CloseSignal signal = 2;    // graceful vs forced
  int32 code = 3;
}

enum CloseSignal {
  CLOSE = 0;                 // graceful succeeded
  KILL = 1;                  // timed out, force-killed
}

message ErrorEvent {
  Level level = 1;
  Module module = 2;
  string msg = 3;
}

enum Level {
  WARN = 0;                  // continues running
  FATAL = 1;                 // will exit; if connection issue, drop as error file
}

enum Module {
  PROCESS = 0;
  CONFIG = 1;
  QUEUE = 2;
  CONNECTION = 3;
}

message Idle {}                // all done, still listening

// Done only sent in response to Exit/Shutdown.
```

## Session Model

Queue then execute. Launcher queues all processes upfront (`Execute` per process, each acked), then `Finished` starts execution in send-order. Bad queue entry → error event on the stream + gRPC error status on the RPC; launcher decides (usually `Shutdown`).

## Semantics (unchanged from JSON draft)

- **`idle`** — all processes exited, queue empty, monitor still listening. Launcher decides next: restart, new execute, or exit. The monitor does NOT exit on its own when work is done.
- **`done`** — only in response to `Exit`/`Shutdown`.
- **Graceful before kill** — stop/restart try graceful close first within the timeout, then escalate to kill (`CloseSignal.KILL`).
- **Fatal errors** — unrecoverable internal crash: monitor exits on its own, writes error file, closes stream. No idle first.

## Version & Handshake

`major.minor.patch` — major = breaking (new proto package), minor = new message types (additive fields), patch = fixes. Launcher calls `Hello` right after connecting; no reply within `--timeout` → monitor is written off. Incompatible major → send `Shutdown`, exit.

After `Restart`, the monitor sends a fresh `Ready` event on the stream with its (possibly new) version — covers monitor self-update mid-session.

## Error Fallback

Connection drops → monitor writes to `--error-file` (same protobuf messages, length-delimited stream). Launcher polls the file on reconnect/startup. Process exit codes: 0 = clean, 1 = connection, 2 = internal crash, 3 = config error. Launcher checks exit code as fallback if error file missing.

RPC-level failures use standard gRPC status codes (`INVALID_ARGUMENT` for bad specs, `ALREADY_EXISTS` for duplicate names, etc.) plus details payload pointing at the related `ErrorEvent`.

## Extensibility

Transport is not hardcoded to one wire format: the service surface stays small and message-based so a secondary payload (e.g. OMMXP) can ride alongside later — either as additional messages in the same stream or a separate service in the same process.

## Example; Happy Path

```
Launcher → Monitor:   Events(filter)                      [stream opens]
Monitor  → Launcher:  Event{ ready, version: "1.0.0" }
Launcher → Monitor:   Execute{ name: "wand", exe: "Z:\\wand.exe", close_with: "game", stdout: CONSOLE }
Monitor  → Launcher:  QueuedAck{ "wand" }
Launcher → Monitor:   Execute{ name: "game", exe: "Z:\\game.exe", stdout: EVENT }
Monitor  → Launcher:  QueuedAck{ "game" }
Launcher → Monitor:   Finished()
Monitor  → Launcher:  Event{ started, "wand", pid 1234 }
Monitor  → Launcher:  Event{ started, "game", pid 5678 }
Monitor  → Launcher:  Event{ output, "game", STDOUT, 1, "Loading..." }
Monitor  → Launcher:  Event{ exited, "game", code 0 }
Monitor  → Launcher:  Event{ closed, "wand", CLOSE, code 0 }
Monitor  → Launcher:  Event{ idle }
Launcher → Monitor:   Exit(code: 0)
Monitor  → Launcher:  Event{ done, FINISHED, code 0 }     [stream ends]
```

## Example; Restart (monitor needs update)

```
Launcher → Monitor:   Events(filter)                      [stream open]
...
Launcher → Monitor:   Restart(kill_timeout: 2)
Monitor  → Launcher:  Event{ closed, "game", CLOSE, code 0 }
Monitor  → Launcher:  Event{ closed, "wand", CLOSE, code 0 }
Monitor  → Launcher:  Event{ ready, version: "1.0.1" }
...
```

## Example; Error (process fails to start)

```
Launcher → Monitor:   Events(filter)                      [stream opens]
Monitor  → Launcher:  Event{ ready, version: "1.0.0" }
Launcher → Monitor:   Execute{ name: "wand", exe: "Z:\\wand.exe" }
Monitor  → Launcher:  QueuedAck{ "wand" }
Launcher → Monitor:   Execute{ name: "game", exe: "Z:\\wrong.exe" }
Monitor  → Launcher:  QueuedAck{ "game" }
Launcher → Monitor:   Finished()
Monitor  → Launcher:  Event{ started, "wand", pid 1234 }
Monitor  → Launcher:  Event{ error, WARN, PROCESS, "failed to start: Z:\\wrong.exe not found" }
Monitor  → Launcher:  Event{ closed, "wand", KILL, code 1 }
Monitor  → Launcher:  Event{ idle }
Launcher → Monitor:   Exit(code: 3)
Monitor  → Launcher:  Event{ done, ERRORED, code 3 }      [stream ends]
```
