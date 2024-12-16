# podman-streamlit

[codeuh's](https://github.com/codeuh) work in progress [Streamlit](https://streamlit.io/) app that uses the [Podman PyPi package](https://pypi.org/project/podman/) for managing containers and images using [Podman](https://podman.io/).

# Run with Podman

I've only tested it running on a RHEL-9 WSL distro with Podman installed and working correctly. I've tested it in rootless mode. I map my local users socket into the container with the only volume mapping in the run command below. If your users is something other than user 1000, then you'll need to determine your socket location and change the host socket mapping in the run command.

I should be able to get it to work via SSH as well, but haven't tested it yet.

You can determin the path to your socket on a Linux machine with the following command:

````shell
podman info | grep sock
````

Expected output will look like this.

````text
path: /run/user/1000/podman/podman.sock
````

Here's the run command!

````shell
podman run -d --name podman-streamlit \
-p 8501:8501 \
-v /run/user/1000/podman/podman.sock:/run/user/1000/podman/podman.sock \
ghcr.io/codeuh/podman-streamlit:main
````
