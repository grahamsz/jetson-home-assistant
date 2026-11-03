# Jetson Home brand images

These images identify the Jetson service connected by this unofficial integration. Jetson's artwork and trademarks belong to Jetson Home; their inclusion does not imply endorsement.

Sources retrieved November 3, 2026:

- `icon.png` and `icon@2x.png`: Jetson's [official 512-pixel website icon](https://jetsonhome.com/_next/static/media/icon-512.a13aaabe.png), linked from the [official website](https://jetsonhome.com/us/press). The original green background and white mark are preserved; the standard version is resized to 256 pixels.
- `logo.png` and `logo@2x.png`: the vector wordmark from the official website header, rendered in black on transparency at 128/256 pixels high.
- `dark_logo.png` and `dark_logo@2x.png`: the same wordmark rendered in white on transparency for dark backgrounds. The green app icon is shared across themes through Home Assistant's standard fallback.

The files follow Home Assistant's [custom integration branding conventions](https://contributors.home-assistant.io/core/integrations/brands/). No extra manifest field or separate branding repository is required for the targeted Home Assistant versions. Live frontend appearance still needs checking in the installed instance.
