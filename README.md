# MOV - Matrix Optimization Visualizer
GUI Tool for visualization of optimized matrix operations graphs

![Main menu](https://github.com/PrzemyslawSamsel/GraphVisualiser/blob/main/Examples/mov_example.gif)

## Goal 
The goal of this project is to develop universal tool for generating signal graph structures. 


## Examples
There are 4 exaples that can be used to familiarize oneself with the tool. All of them represents differend cases and can be accessed in a tools section in the file menu bar.
1. The *Example 1* is an easy 3 matrices multiplication
2. The *Example 2* is much more complex involving 7 matrices and works best when "stretch columns" parameter is unticked. The tool can have a problem with more complex structures so it is highly recomend to untick that parameter first when the graph looks bad. 
3. The *Example 3* has the same problem as previouse one with the "stretch columns" parameter. This graph is even more complex involving 9 matrices and can take more time to load.
4. The *Example 4* is an 4 matrices multiplication but with different number of input and output size. It also works best wit "stretch columns" parameter unmarked.

## Plot parameters

The tool provides user with few parameters that can be manipulated in order to change the look of the structure or to make it more readable. This parameters are:
* Column offset - changes the column offset
* Vertical offset - changes the vertical offset
* Bridge size - changes the size of the bridge, that is the short line between the in/out data and the operation.
* Lables and fonts
  * x - changes the literal of the vector with input data
  * y - changes the literal of the vector with output data
  * sum - changes the literal of the operations presented in circles
  * font size - changes the font size
* Stretch columns - streaches the columns so that the input and output data is positioned in the middle 
* Show grid - shows grid for easier manipulation

## Loading from files

Matrices can be loaded from files separately, filled manually, or filled from files automatically based on their names (must match!): 

![Main menu](https://github.com/PrzemyslawSamsel/GraphVisualiser/blob/main/Examples/fromfiles_mov.gif)

## Exporting graph to a file
You can export generated graph by right clicking anywhere on the plot and choosing option "Export". This is shown on the graphic below:

![Main menu](https://github.com/PrzemyslawSamsel/GraphVisualiser/blob/main/Examples/export_data.gif)
