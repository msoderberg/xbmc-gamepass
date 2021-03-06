# NFL Game Pass/Rewind XBMC Plugin #
**version 0.5.0 — Jerry Rice Edition**

Before reading any further, please understand that while this plugin does
work, not all features are supported (or fully tested) and it should be
regarded as an alpha release. It may crash, spay your puppy, and/or cause your
oven to not heat to 400° F properly. The plugin is under development, and needs
a whole lot of love.

If you're interested in helping out, just drop us an email or send a pull
request. Patches and (constructive) input are always welcome.

## Any Dependencies? ##
Until this addon is part of an official XBMC repository (hopefully sometime
soon), dependencies will not be installed automatically.
 * xmltodict (http://mirrors.xbmc.org/addons/frodo/script.module.xmltodict/)
 * Requests (http://mirrors.xbmc.org/addons/frodo/script.module.requests2/)

## What is NFL Game Pass? ##

NFL Game Pass is website that allows those of us outside of the US (or with IPs
outside of the US ;-) to watch NFL games. Archives of old games stretch back to
2009, coaches film (22 man view) is available, as is audio from each team's
radio network. Overall, it is a sweet service offered by the NFL for those of
us who must have our American Football fix.

## What is NFL Game Rewind? ##

NFL Game Rewind is the USA version of Game Pass, but the service is blacked out
during live games, and doesn't have access to NFL Network - Live, many of the
archived shows, etc.

## Why write a plugin for XBMC? ##

First off, we love XBMC and like consuming media through its interface.
Secondly, while there is a nice Flash interface, it's... well... written in
Flash. The client is a resource hog, the interface is frequently buggy, and it
includes a bunch of bells and whistles (social media, for example) that are
simply distracting. We're here to watch a game, nothing else.

## What features are currently supported? ##

By now, most core features are supported.

 * Archived games from 2011 to 2013 (both full and condensed)
 * Live games (requires Gotham)
 * NFL Network - Live (requires Gotham)
 * A Football Life
 * NFL Films Presents
 * NFL Gameday
 * Playbook
 * NFL RedZone Archives
 * NFL RedZone - Live (requires Gotham)
 * Sound FX
 * NFL Total Access

Currently unsupported features:
 * Archived games prior to 2011
 * Alternate team audio
 * Coaches film (22 man view)
 * Coaches Show
 * Superbowl Archives
 * Top 100 Players

## Release names ##

Want a release to be named after your player/coach of choice? Contribute to the
project in some way (code, art, debugging, beer, brazen — yet effective —
flattery, etc), and we'll gladly name a future release after them.

## Roadmap ##

A rough roadmap follows:

* Continue work towards feature completeness
* Stabilize Game Rewind support
* Refactor code to be more XBMC agnostic
