# map-proxy

## Introduction

map-proxy is a URL proxy/translator for map tiles. It can be used for different purposes such as:
- Allow a mapping software that work with OSM map tile servers to use servers that do not conform to OSM standard (for example ign.fr)
- Add some additional data (such as cookies) to requests when the mapping software cannot add them (such as authentication keys or cookies)

As of today, map-proxy only process/translate the tile http request. It doesn't perform any graphical convertion (resize, format change) or even geographical transformation. This may be added in the future if I have time and need.

map-proxy is simple and do not include a lot of checkings. It may crash or hang if requests are not provided are expected or if the remote map server do not answer as expected.

## Principle of operation

map-proxy will create a **non-secured** web server based on Python built-in `http.server` class. For each entry in the configuration JSON file, map-proxy will listen to an OSM map tile GET request and pass-on the request to the real server by translating the URL as specified.

## map-proxy command-line arguments

map-proxy can be ran with the below optional command-line arguments
- `-c, --cfg configfile.json` to specify a JSON configuration file. When omitted, map-proxy will try to read `map-proxy.json` from the current directory.
- `-p, --port portnumber` to specify the port number on which map-proxy will create the web server. When mmited, map-proxy will create a webserver on port 8888.

## Configuration file format

map-proxy configuration file is a JSON file which starts as an array of descriptor. Each descriptor is a key-value pair list (aka dictionary) which includes the following items:

- An ignored `__comment` key for the purpose of documentation of the JSON file.
- A mandatory `path` string which specify on witch path (single level) map-proxy will listen for this map descriptor.
- A mandatory `url` template string which specify the URL to the real tile server. The url template contains some variables (in `{varname}` format) that will be substituted before map-proxy makes the tile requests. There are standard variables from the incoming OSM request (such as `zoom`, `x` and `y`), internal to map-proxy (such as `serverpart`) or customs variables from the JSON to specifies additional parameters such as authentication keys.
- An optional `params` string which, if present, will be concatenated at the end of the url prefixed by a question mark.
- An optional `variables` key-value pair list (dictionary) which provides custom variables to be substituted in the URL.
- An optional `headers` key-value pair list which provides additional headers to be added to the GET request to the map server. This is usefull to provide `Cookie` or `Referer` headers that may be required by some servers.
- An optional `serverpart` array which, if present, will provide a `serverpart` variable to be used in the url.
- `minzoom` and `maxzoom` are not used for now and can be set for comment.

### Expected OSM style request

map-proxy expects GET request in the form of `GET http://ip.address:port/<path>/<zoom>/<x>/<y>.<filetype>` where:
- `<path>` is one of the single level path from the configuration file. A request to an non defined path will be rejected with a 404 "Fie not found" HTTP error.
- `<zoom>`, `<x>`, `<y>` specify the tile requested by its zoom level and it x,y location. For more details on the zoom, x and y, please refer to Open Street Map wiki.
- `<filetype>` is optional file extension. map-proxy doesn't do anything specific with it but it can be used a variable for substitution in the url.

All above elements will be available as variables for substitution in the url to the real server.

Example valid requests: `GET http://localhost:8888/strava-heatmap/15/16476/12344/png`

### URL template and variables

The URL template is the URL to the real map server where some parts are variables. Before making the request to the map server, map-proxy will substitute the variables with their real values such as:
- `zoom`, `x`, `y` values from the OSM-style incoming request
- Variables from the optional custom variables list
- built-in `serverpart` variable when defined (see details below)

### HTTP headers

Optional headers can be added to the request. As of today only those headers will be in the request to the map server. Incoming headers are **not** forwarded (todo). Specifying headers is useful in various cases to specify some elements that are required for authentication to the web server.

### serverpart

Some map servers actually provide multiple servers by adding a number or a letter to the server name. For exemple `heatmap-external-a.strava.com` and `heatmap-external-b.strava.com`. This is usefull to load-balance the request to multiple servers and avoid congestion. If the configuration element `"serverpart"` is provided as a list of server parts (either numeric as `[0, 1, 2, 3]` or string as `["a", "b", "c"]`), on each request, map-proxy will use one the provided entry to define a variable named `serverpart` that will be used in substitution. The exact list entry that is used is _x modulo len(serverpart)_.

## Exemple configuration entry : Strava heatmap

The sample configuration entry for Strava heatmap is as below:
``` json
 {
        "__comment": "You must retrieve the Cookie from an acctual web browser session once loggued into your Strava accunt, and insert the 3 required cookies in the headers session below.",
        "path": "strava-heat",
        "url" : "https://heatmap-external-{serverpart}.strava.com/tiles-auth/{sport}/{color}/{zoom}/{x}/{y}.png",
        "params": "px=256&v=19",
        "serverpart" : ["a","b"],
        "variables" : {
            "sport" : "ride",
            "color": "red"
        },
        "headers" : {
            "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "referer" : "https://www.strava.com/",
            "origin" : "https://www.strava.com/",
            "cookie" : "CloudFront-Policy=*******; CloudFront-Key-Pair-Id=*******; CloudFront-Signature=*******~Ivd~L~wrCqCoSCNvL7v8-DFXbj27j2p7J9qkDm7RHDDwsT05Fjsk8rUvkt2btoseDKkqXW0Nas3AwSp-aGbF7zymM67sUn3CRtcG7tszQJn2K0ONGc2OmUd4wn534rZWRLVwdre~5EG3IEK0E-iBHUNrMlIbhF~FbGoaX44SiOMeZ43r8Ef1xXDfC1kokQE1fjAS4kJDcRbBNoCTVfyZ52qkxdjIjqa8uInjjo1TmBR3RO01oET4JiesYFush3~XPL9j27kNaZl3X6cxuWjQZbKoCb6AYt~C-tg8zGO7VODn~h1y~szf1Ll2yjYB0IR3qQQ__"
        },
        "minzoom" : 1,
        "maxzoom" : 15
    }
```

Let's see each element one-by one.

The `__comment` just describes the entry, reminding you that you will need to get some Cookie values from your browser to define the `cookie` header entry.

The `path` entry specify that map-proxy will apply the Strava Heatmap transformations to any OSM-style request starting with `/strava-heapmap`.

The URL template will be used by map-proxy to build the effective request to the Strava server.
- The server name include a `{serverpart}` variable which with the `"serverpart" : ["a","b"]` configuration item will be replaced by either `a` or `b` to balance the request onto 2 different servers.
- The `{sport}` and `{color}` variables will be subsituted by the matching variables. Using variables for this makes it more easy to tweak the file if you want to change the color or the sport you are interrested in. For more details, please refer to Strava documentation.
- `{zoom}`, `{x}` and `{y}` will be substituted with the values from the incoming request

The `params` string `px=256&v=19` will be prefixed by a `?` and added at the end of the URL sent to the tile server. This allows to easily add some parameters to the GET request. Concatenation is done before variables are susbsituted so `params` can also contains variables. This helps to make the URL more readable although parameters could have been added directly in the URL like it was done in v0.1.0. In this particular exemple, it instruct Strava server to return 256x56 pixels tiles which is the most common.

The custom `variables` entries specifies the values to be substituted for `{sport}` and `{color`} in the URL. It could have been hardcoded in the URL but this helps making the entry more readable.

The `headers` entries will be added to the request.
- `user-agent` let Strava believe the request is made from a browser.
- `referer` and `origin` states that the request is made through Strava web site.
- `cookie` adds the authentication cookies for Strava to accept the request. You can extract the proper values once you are logged into your Strava account with your browser (for example using Chrome or Firefox developper's tool). As of today, Heatmap are not restricted to Strava Premium users.

As explained, `minzoom` and `maxzoom` are currently not used bt could be used in the future.

## Using with TwoNav Land

I mainly using this tool with [TwoNav Land](https://www.twonav.com/en/software/land), a commercial mapping software to prepare my hiking and biking trips. I have no affiliation with TwoNav, just like their software.

In the `twonav-land-map-samples` you will find some sample `*.cosm` map files that can be used in TwoNav with the sample `map-proxy.json` configuration file.

## How to build configuration for site XXXX

**I will not provide any help on how to configure map-proxy for site XXX or YYY, do your homework first.**

Especially I will not answer to any question regarding circuventing access to a licensed map server (I would probably have no idea on how to do so). **map-proxy is not meant to do that**. When authentication is required, you must have the needed information to configure map-proxy.

Generally, logging and navigating the site with Chrome or Firefox developper tool open should provide the needed information. In some cases, the request expected by the remote server may be complex and may not be supported with map-proxy simple scheme. If such a method is openly documented, I may be able to extended map-proxy capabilities.

Only request that can be related to a bug in map-proxy may be answered depending on my spare time.
