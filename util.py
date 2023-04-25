import subprocess
import os
import sys
from typing import Callable
from urllib import request

SCRIPT_PATH=os.path.dirname(os.path.realpath(__file__))
WINEPREFIX = os.path.join(os.getenv("STEAM_COMPAT_DATA_PATH"), "pfx")

def pip(command:str) -> int:
  pip_pyz = os.path.join(SCRIPT_PATH, "pip.pyz")

  if not os.path.isfile(pip_pyz):
    log("pip not found. Downloading...")
    request.urlretrieve("https://bootstrap.pypa.io/pip/pip.pyz", pip_pyz)

    if not os.path.isfile(pip_pyz):
      log("CRITICAL: Failed to download pip. Exiting!")
      sys.exit(1)

  process = subprocess.Popen("python3 {} {}".format(pip_pyz, command), shell=True, stdout=subprocess.PIPE)
    
  for line in iter(process.stdout.readline,''):
    if line == None or line == b'':
      break
    log(line.decode("utf8"))

  return process.wait()
  

def log(message:str):
  if "WEMOD_LOG" in os.environ:
    message = str(message)
    message = message if list(message)[-1] == "\n" else message + "\n"
    with open(os.getenv("WEMOD_LOG"), "a") as f:
      f.write(message)

def popup_execute(title:str, command:str, onwrite:Callable[[str], None] = None) -> int:
  import PySimpleGUI as sg
  import subprocess as sp

  sg.theme("systemdefault")

  text_str = [""]
  text = sg.Multiline("", disabled=True, autoscroll=True, size=(80, 30))
  layout = [ [text] ]
  window = sg.Window(title, layout, finalize=True)
  exitcode = [-1]


  def process_func():
    process = sp.Popen(command, stdout=subprocess.PIPE, shell=True)
    for line in iter(process.stdout.readline,''):
      if line == None or line == b'':
        break
      s_line = line.decode("utf8")
      log(s_line)
      text_str[0] = text_str[0] + s_line + "\n"
      if onwrite != None:
        onwrite(s_line)
    exitcode[0] = process.wait()


  window.perform_long_operation(process_func,"-PROCESS COMPLETE-")

  while True:             # Event Loop
      event, values = window.read(timeout=1000)
      if event == "-PROCESS COMPLETE-":
          break
      elif event == None:
          sys.exit(0)
      else:
          if(len(text_str[0]) < 1):
              continue
          text.update(text_str[0])

  window.close()
  
  return exitcode[0]

def popup_dowload(title:str, link:str, file_name:str):
    import PySimpleGUI as sg
    sg.theme("systemdefault")

    status = [0,0]

    cache = os.path.join(SCRIPT_PATH, ".cache")
    if not os.path.isdir(cache):
        os.makedirs(cache)

    progress = sg.ProgressBar(100, orientation="h", s=(50,10))
    text = sg.Text("0%")
    layout = [  [progress], [text] ]
    window = sg.Window(title, layout, finalize=True)

    def update_log(status:list[int], dl:int, total:int) -> None:
        status.clear()
        status.append(dl)
        status.append(total)
    
    file_path = os.path.join(cache, file_name)
    download_func = lambda: download_progress(link, file_path, lambda dl,total: update_log(status, dl, total))

    window.perform_long_operation(download_func,"-DL COMPLETE-")

    while True:             # Event Loop
        event, values = window.read(timeout=1000)
        if event == "-DL COMPLETE-":
            break
        elif event == None:
            sys.exit(0)
        else:
            if(len(status) < 2):
                continue
            [dl,total] = status
            perc = int(100 * (dl / total)) if total > 0 else 0
            text.update("{}% ({}/{})".format(perc, dl, total))
            progress.update(perc)

    window.close()
    return file_path

def download_progress(link:str, file_name:str, set_progress):
  import requests

  with open(file_name, "wb") as f:
      response = requests.get(link, stream=True)
      total_length = response.headers.get('content-length')

      if total_length is None: # no content length header
          f.write(response.content)
      else:
          dl = 0
          total_length = int(total_length)
          for data in response.iter_content(chunk_size=4096):
              dl += len(data)
              f.write(data)
              if set_progress != None:
                set_progress(dl, total_length)

def winetricks(command:str, proton_bin:str) -> int:
  winetricks_sh = os.path.join(SCRIPT_PATH, "winetricks")
  command = "export PATH='{}' && ".format(proton_bin) + \
    "export WINEPREFIX='{}' && ".format(WINEPREFIX) + \
    winetricks_sh + " " + command
  
  resp = popup_execute("winetricks", command)
  return resp


def exit_with_message(title:str,exit_message:str, exit_code:int = 1) -> None:
  import PySimpleGUI as sg
  sg.theme("systemdefault")

  log(exit_message)
  sg.popup_ok(exit_message)
  sys.exit(exit_code)


if __name__ == "__main__":
  popup_execute("HELLO", "sh -c \"echo hello && sleep 5 && echo bye\"")