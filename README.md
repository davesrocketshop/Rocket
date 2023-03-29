## FreeCAD Rocketry Workbench

A rocket design workbench for FreeCAD

![Demo Components](Resources/rwb_alphaIII.png)

## Install

### Automatic

The Rocket Workbench is available as part of the Addon Manager. See https://wiki.freecadweb.org/Std_AddonMgr
  
### Manual

<details>
  <summary>Expand for Manual install instructions</summary>

1. Obtain your user's default FreeCAD folder by typing the following in to the FreeCAD Python console `FreeCAD.ConfigGet("UserAppData")`
2. Open a shell terminal
3. Switch to folder in step 1 and append the `Mod/` subfolder ex: `cd ~/.FreeCAD/Mod`
4. Type `git clone https://github.com/davesrocketshop/Rocket`

The Rocket workbench will automagically download to your local machine. 

5. Restart FreeCAD for changes to take place.
6. Rocket WB should now be available in the workbench dropdown menu.

**Note:** In order to keep Rocket WB up-to-date you'll need to follow Steps 2 and 3. But for step 4 replace with `git pull`  
Again, restart FC to use the latest changes.

</details>

## Internationalization

This workbench has been written with multiple language support. If you are willing to provide a translation to your native language please open an issue and we'll work to get that done.

## Reporting issues

The best method for reporting problems is to create a new issue in [GitHub](https://github.com/davesrocketshop/Rocket/issues). Please include information
such as the development branch you're using, instructions on how to reproduce the error, and where relevant a copy of the file in which the issue was encountered.
The more information you provide the easier it will be to pinpoint the problem.

## Feedback

For any feedback, features, and discussion please refer to the Rocketry workbench FreeCAD [forum thread](https://forum.freecadweb.org/viewtopic.php?f=8&t=54496).

## Developers

David Carter AKA [@davesrocketshop](https://github.com/davesrocketshop)

## Contributions

Component database originally taken from the Open Rocket project. (https://github.com/openrocket/openrocket) Whole sections of the Open Rocket code have been shamelessly plagiarized.

Now using the improved and curated parts database by Dave Cook instead (https://github.com/dbcook/openrocket-database)

Portions of the pyatmos module by Chunxiao Li are included with this software (https://github.com/lcx366/ATMOS)

Icon by Adrien Coquet from <a href="https://thenounproject.com/browse/icons/term/center/" target="_blank" title="center Icons">Noun Project</a>

[![Total alerts](https://img.shields.io/lgtm/alerts/g/davesrocketshop/Rocket.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/davesrocketshop/Rocket/alerts/)  [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/davesrocketshop/Rocket.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/davesrocketshop/Rocket/context:python)

## License
LGPLv2.1 (see [LICENSE](LICENSE))