name: Bug report
description: Create a report to help us improve
title: '[Bug] The WeMod launcher fails with error X'
labels: ["bug"]
body:
  - type: textarea
    id: bug-description
    attributes:
      label: Describe the bug
      description: A clear and concise description of what the bug is.
      placeholder: Describe the issue you encountered.
    validations:
      required: true

  - type: textarea
    id: steps-to-reproduce
    attributes:
      label: Steps to reproduce
      description: Detailed steps to reproduce the behavior.
      placeholder: |
        1. Go to '...'
        2. Click on '....'
        3. Scroll down to '....'
        4. See error
    validations:
      required: true

  - type: textarea
    id: expected-behavior
    attributes:
      label: Expected behavior
      description: A clear description of what you expected to happen.
      placeholder: Describe what you expected to occur.
    validations:
      required: true

  - type: textarea
    id: screenshots
    attributes:
      label: Screenshots (if applicable)
      description: Add screenshots to help explain your problem.
      placeholder: Drag and drop or click to upload screenshots.
    validations:
      required: false

  - type: textarea
    id: system-information
    attributes:
      label: System Information
      description: Details about your operating system and environment.
      placeholder: |
        - OS: [e.g. Windows 10, macOS 11.5]
        - Version: [e.g. 1.2.3]
    validations:
      required: true

  - type: textarea
    id: additional-context
    attributes:
      label: Additional context
      description: Any other relevant information about the problem.
      placeholder: Add any other context about the problem here.
    validations:
      required: true
