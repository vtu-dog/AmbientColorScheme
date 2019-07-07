# AmbientColorScheme
Switch Sublime Text 3 color scheme based on ambient light readings

## Motivation

I was tired of switching between Sublime's color schemes while working in differently lit environments. This package checks for changes in light sensor's readings and changes the color scheme accordingly.

## Compatibility

The plugin will only work on Macbooks running MacOS, as the light sensor code included in the project as a shared library uses OSX-specific calls. If you know of a way to support other LMUs and are willing to test the changes, GitHub issues and pull requests are greatly appreciated!

## Developer info

If you stumbled upon this project and wanted to make use of the LMU code, it is included in the `src` directory and can be compiled as a shared library via:
```
$ clang -c lmu.c -o lmu.o
$ clang -shared -framework IOKit -o lmulib.so lmu.o
```

## Additional info

The project was tested on macOS 10.14.5 Mojave and Sublime Text version 3.2.1, build 3207.
