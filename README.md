
# iCUE Custom Visualizer

The iCUE Custom Visualizer is a program that displays the json needed for [CUEORGBPlugin](https://github.com/expired6978/CUEORGBPlugin) 

## Features

- Displays the LED positions of custom devices in iCUE using CUEORGBPlugin format
- Realtime updates from the json provided
- Bugs, alot of bugs

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/your-username/icue-rgb-device-viewer.git
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

## Usage

1. Ensure that you have set the directory for `image_path` and `json_path`
2. Launch the program
3. Either use a text editor and edit the json that way or use the tools provided inside the program


## Important Commands

```
Left-Click - Selects block
Move - Moves selected block
Right-Click - Drag inside the selected block to scale
Ctrl-s - Saves to the json
Ctrl-d - Duplicates the selected block
```