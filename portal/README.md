# EPIPortal

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 11.0.2.

## Pre-requisites for installation

1. Install NPM 
Angular requires Node.js in your system. You can download Node.js from here if you do not have it installed [Node.js](https://nodejs.org/en/)

2. Install Angular CLI 
Check @angular/cli version in your system.
If you already have it installed, make sure it uses the same version as that of the project.
Otherwise, run the following command in command prompt:
npm install -g @angular/cli@11.0.2

3. Install all required npm packages for the project
Navigate to the project folder in command prompt.
Run the following command in command prompt:
npm install

## Development server

Run `npm start` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files. 

The app will start with a proxy. The settings of the proxy can be modified in proxy.conf.json.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `--prod` flag for a production build.

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via [Protractor](http://www.protractortest.org/).

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.


# Folder Structure Overview

The following sections describe the folder structure of custom folders in the solution and the contents within it. 

Information about each folder/file is given in the following format:
Folder/File Name -> **Description about the contents**

## EMA Design System Folder Structure Overview

|-- Portal -> **This folder hosts the Web portal's source code.**
    |-- projects
        |-- ema-component-library -> **The root folder of an Angular library containing the module that makes up the EMA design system.**
            |-- src
                |-- lib
                    |-- atoms -> **Folder containing basic UI components required by the portal.**
                    |-- molecules -> **Folder containing angular components made of components from the atoms folder.**
                    |-- layouts -> **Folder containing common UI elements to build the layout of the portal. Ex: Header, Footer, etc...**
                    |-- scss -> **Folder containing scss files common to all components.**
                    |-- ema-component-library.module.ts -> **File hosting the angular module of the design system.**
                    |-- ema-design-system.scss -> **Global scss file to import all common scss files into.**
                    |-- ema-theme-variables.scss -> **Gloabl scss file that contains all scss theme related variables.**

## EPI Portal Folder Structure Overview

|-- Portal
    |-- src -> **Folder containing the application's source code.**
        |-- app
            |-- models -> **Folder containing shared classes, interfaces and enums used throughout the solution.**
            |-- pages -> **Folder containing angular components and modules that make up a particular page. Components from the EMA design system project are used to make these pages.**
            |-- shared-pipes -> **Folder containing shared pipes used throughout the solution.**
            |-- shared-services -> **Folder containing shared services used throughout the solution.**


# Making API calls

This angular application uses a proxy. The configurations of the proxy can be obtained in the `proxy.conf.json` file. 

Please make sure your server's base url is the same as the one present in the `target` property of the `proxy.conf.json`.
For example, if your server's url is `xyz.com`, the `target` property should be as follows:
`"target" :"xyz.com/"`

While making your API calls prefix your call with `api/` instead of the server's base url.
For example, if you want to make a call with the url `xyz.com/Bundle`, the url in the angular application should be `api/Bundle`.
