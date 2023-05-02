# Welcome to Connect Extension project CloudBlue Connect Transformations Extension Mock for E2Es

## Next steps

You may open your favourite IDE and start working with your project, please note that this project runs using docker.  
In the root directory of the project you could find *.eaas_transformations_dev.env.__dist__* file, 
which contains example data for configuring your authentication credentials. Before you start using the extension, 
it is essential to rename this file to *.eaas_transformations_dev.env* and update it with your correct authentication 
information.  
This step is crucial to ensure a seamless connection and authentication process when interacting with the application. Please make sure to replace the example data with your accurate credentials to avoid any potential issues during the authentication process.  

In order to start your extension as a standalone docker container first of all you need to build the docker image for your project. To do that run:

```sh
$ docker compose build
```

Once your container is built, you can access the project folder and run:

```sh
$ docker compose up eaas_transformations_dev
```

> please note that in this way you will run the docker container and if you do changes on the code you will need to stop it and start it again.


If you would like to develop and test at the same time, we recommend you run your project using the command:

```sh
$ docker compose up eaas_transformations_bash
```

Once you get the interactive shell an help banner will be displayed to inform you about the included tools that can help you with the development of your extension.


Additionally, a basic boilerplate for writing unit tests has been created, you can run the tests using:

```sh
$ docker compose up eaas_transformations_test
```


## Community Resources

Please take note of these links in order to get additional information:

* https://connect.cloudblue.com/
* https://connect.cloudblue.com/community/modules/devops/
* https://connect.cloudblue.com/community/sdk/python-openapi-client/
* https://connect-openapi-client.readthedocs.io/en/latest/
* https://connect-eaas-core.readthedocs.io/en/latest/
