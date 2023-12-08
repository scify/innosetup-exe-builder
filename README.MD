# Inno Setup-exe-builder

This API provides the ability to build a Windows executable installer.

Typically, this is accomplished using [Wine](https://www.winehq.org/) and [InnoSetup](https://jrsoftware.org/isinfo.php) on the same server. However, maintaining this setup has become increasingly difficult due to compatibility issues with newer 64-bit distributions.

We created a thin flask application that serves as the wrapper for a Docker-based solution, and acts as a builder for .exe installers.

## Introduction

This guide explains how to create a Windows executable using Inno Setup and Wine, utilizing a temporary Docker container as the builder. This functionality is utilized by our Flask application to generate the Windows executable installer at the request of the client application.

## Api routes exposed

This api exposes a `/compile` route, which takes 2 parameters:

* `path`: the absolute path of the directory that Innosetup config file resides
* `file_name` (OPTIONAL): the file name of the Innosetup config file (.iss file)

## How to Setup/Run this app

To run this app we will use gunicorn.

### Create a virtual environment and install the dependencies


To set up the environment and run the application, follow these steps:

1. Install `virtualenv` by visiting the [official installation guide](https://virtualenv.pypa.io/en/latest/installation.html).
2. Create a new environment by running `virtualenv env_name`. Refer to the [user guide](https://virtualenv.pypa.io/en/latest/user_guide.html) for more details.
3. Activate the environment by running `source /path/to/newly/created/env/`.
4. Install the required dependencies by running `pip install -r requirements.txt`.
5. Navigate to the `project_root/src` directory.
6. Run the application using the following command:
    ```bash
    gunicorn --conf gunicorn_conf.py --bind 0.0.0.0:<local-port> main:app
    ```
7. Test a `POST` request to [http://0.0.0.0:<local-port>/compile](http://0.0.0.0:<local-port>/compile)

## Instructions to set up building exe installer manually

#### Creating Installers with Docker

To create the installers for the required client application, we will utilize a Docker container. 

This approach allows us to run commands within the container and generate the installer in the mounted directory.

#### Setup Instructions

1. Install Docker by following the instructions provided in the [official Docker documentation](https://docs.docker.com/engine/install/ubuntu/).
2. Add your user to the Docker group to ensure proper permissions.
3. Pull the required Docker image by executing the following command:
    ```bash
    docker pull amake/innosetup:innosetup6
    ```
4. Test that the Docker image is working correctly by running the following commands:
    ```bash
    su - server_user
    cd /path/to/dir/with/iss-file
    docker run --rm -i -v $PWD:/work amake/innosetup:innosetup6 <iss-file-name>
    ```

    **Note:** Make sure to include the Docker image tag to avoid inconsistent results.

#### Bash Script for Convenience

```text
#!/usr/bin/env bash

exec docker run --rm -i -v $PWD:/work amake/innosetup:innosetup6 "$@"
```

#### Access problems when creating file

Depending on configured permissions on current directory, the container may not have write access to the mounted folder. This means, that will not be able to create the "Output" folder, and would not be able to create files inside.

To mitigate that we could expand our script to:
1. create a folder "Output"
2. Add write permission to any 777
3. Create executable
4. Change back the permissions

```text
#!/usr/bin/env bash

# Create the Output directory if it doesn't exist
if [ ! -d "Output" ]; then
  mkdir Output
  chmod 777 Output
fi
exec docker run --rm -i -v $PWD:/work amake/innosetup:innosetup6 "$@"
chmod 775 Output
```

## Credits

- [SciFY Dev Team](https://github.com/scify)

## License

The Apache Licence. Please see the [Licence File](LICENCE.md) for more information.