<p align="center">
  <img src="./figures/overview.jpg" width="100%" alt="GIGAPIXEL-WOODBOT-logo">
</p>
<p align="center">
    <h1 align="center">Gigapixel Woodbot</h1>
</p>
<p align="left">
    This is the repository for our custom-built system that we call Gigapixel Woodbot. This system is a modular imaging system that enables automated scanning of large wood surfaces. The frame of the robot is a CNC (Computer Numerical Control) machine to position a camera above the objects. Images are taken at different heights for stacking and in both X and Y directions, with a small overlap between consecutive images and merged, by mosaic stitching, into a gigapixel image. Multiple scans can be initiated through the graphical application, allowing the system to autonomously image several objects and large surfaces.
</p>

<p align="center">
	<!-- local repository, no metadata badges. --></p>
<p align="center">
		<em>Built with the tools and technologies:</em>
</p>
<p align="center">
    <img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Docker-2496ED.svg?style=default&logo=Docker&logoColor=white" alt="Docker">
    <img src="https://img.shields.io/badge/SciPy-8CAAE6.svg?style=default&logo=SciPy&logoColor=white" alt="SciPy">
    <img src="https://img.shields.io/badge/pandas-150458.svg?style=default&logo=pandas&logoColor=white" alt="pandas">
	<img src="https://img.shields.io/badge/NumPy-013243.svg?style=default&logo=NumPy&logoColor=white" alt="NumPy">
    <img src="https://img.shields.io/badge/Flask-000000.svg?style=default&logo=Flask&logoColor=white" alt="Flask">
    <br>
	<img src="https://img.shields.io/badge/GNU%20Bash-4EAA25.svg?style=default&logo=GNU-Bash&logoColor=white" alt="GNU%20Bash">
    <img src="https://img.shields.io/badge/HTML5-E34F26.svg?style=default&logo=HTML5&logoColor=white" alt="HTML5">
	<img src="https://img.shields.io/badge/JavaScript-F7DF1E.svg?style=default&logo=JavaScript&logoColor=black" alt="JavaScript">
	<img src="https://img.shields.io/badge/YAML-CB171E.svg?style=default&logo=YAML&logoColor=white" alt="YAML">
	<img src="https://img.shields.io/badge/JSON-000000.svg?style=default&logo=JSON&logoColor=white" alt="JSON">
</p>
<br>

#####  Table of Contents

- [ Overview](#-overview)
- [ Workflow](#-workflow)
- [ Getting Started](#-getting-started)
- [ Cite our work](#-cite-our-work)
- [ License](#-license)

---

##  Overview

This repository contains the Gigapixel Woodbot, a custom-built, modular imaging system designed for the automated scanning of large wood surfaces. The system leverages a CNC (Computer Numerical Control) machine as its frame, which positions a camera and a laser height sensor above the objects. The robot operates along three axes, capturing images at various heights to create detailed gigapixel images of wooden objects. This method compensates for the camera's limited depth of field and ensures high-quality, focused images.

The images are captured in both the X and Y directions with small overlaps, and are combined using extended focus imaging (EFI) to correct for vignetting and depth. A mosaic stitching algorithm merges these images into a seamless gigapixel image. The modularity of the system, due to its container-based approach, allows for the integration of other camera systems and sensors, optimizing image quality and enabling further research applications in wood and wood technology.

A graphical web application has been developed to control the robot, calibrate its components, and initiate multiple scans, allowing for autonomous operation. This feature makes the system user-friendly for researchers who can scan several objects or large surfaces without manual intervention. The system is ideal for digitizing large collections of wood samples, such as increment cores and wood discs, similar to commercial solutions like GIGAmacro and Hirox. The independence of the motion control from the imaging process means that a variety of contact or non-contact sensors can be added to the toolhead, providing flexibility for future research needs. 

---

## Workflow

![Domain diagram of the software architecture of the Gigapixel Woodbot. Each rectangle represents a container. The numbers at the arrows represent the communication between containers](/home/galileog/Documents/Gigapixel-Woodbot/figures/domain_diagram.jpg)

The figure above shows the domain diagram of the software, which makes use of the Docker container. Docker is an open source platform used to package software applications into containers, which are lightweight and portable environments in which applications can run, with all its dependencies regardless of the environment in which it is placed. Communication between the different containers is indicated by arrows. 

### Python Acquisition Container
The Python acquisition container communicates directly with the camera and laser sensor. In addition, the container establishes a connection with the LinuxCNC container to operate the CNC machine. All images are stored on the local hard drive of the workstation. When image acquisition finalizes, the metadata of these images is sent to the DIS. This allows the analysis container to retrieve them later. Finally, all acquisition functionality is available via REST (REpresentational State Transfer) calls, making it addressable via the GUI.

### LinuxCNC Container
The LinuxCNC container provides control of the CNC machine (arrow 3). LinuxCNC is an open-source software platform widely used for CNC machines and robotic applications. It provides a Python library to write automated scripts for the machine to execute.

### Document Image Store Container
To manage the large amount of images, the system has a Document Image Store (DIS) container. This container runs a MongoDB database and receives metadata from images taken via the acquisition container. The advantage of using a DIS is that it is easy to scale, and the stored data can be managed in a structured manner. The metadata of images can be queried by other containers, such as the analysis container and the GUI container, which later retrieves the images.

### Python Analysis Interface Container
Once the acquisition task has finished, the images pass through an analysis pipeline. A container ensures that this pipeline is executed and observes the DIS for new or changed data. If a new document is added or an existing document is changed, the container will notice this change. The Python analysis interface container communicates with the EFI, lens correction, and stitching containers via REST calls. Additionally, this analysis container has a REST API that enables interaction with the GUI.

When the container detects a change in the DIS, it forwards the tasks to the appropriate container.

### Extended Focus Imaging Container
This container controls the Extended Focus Imaging (EFI) algorithm developed by Petteri Aimonen (GitHub repository [PetteriAimonen/focus-stack](https://github.com/PetteriAimonen/focus-stack)), based on the work of \citep{forster2004complex}. The application is written in C++, uses OpenCV, and is GPU-accelerated by the use of the OpenCL API.

### Lens Correction Container
This container controls the lens correction algorithm, correcting for vignetting. The telecentric lens is designed to work optimally with camera sensors that have a diagonal size of 21.5 mm; however, the camera used has a sensor size of 26 mm, resulting in mechanical vignetting. It also shows optical vignetting due to the shape of the lens.

Mechanical vignetting was solved by cropping the detector size to 3380 x 3380 pixels (instead of the original 4096 x 4096 pixels), and optical vignetting was solved by correcting the images using flat-field images from a uniform object and correcting them using the BaSiC Python library \citep{peng2017basic}.

### Stitching Container
The final step is performed in the stitching container. The stitching algorithm used is the Microscopy Image Stitching Tool (MIST) \citep{chalfoun2017mist}. It is a direct-based algorithm written in Java and is a hybrid implementation that uses both the CPU and the GPU. Communication with the GPU is done via NVIDIA® CUDA. By communicating with the GPU, the stitching process is fast and efficient.

### GUI Container
To control the Gigapixel Woodbot, a GUI runs in a separate container. The application is hosted by an NGINX web server, a popular web server known for its high performance, reliability, and scalability. The application is written in HTML, CSS, and JavaScript and uses the open-source toolkit Bootstrap for basic theming. Bootstrap's pre-styled components make the development tool easy to use and lead to faster development. The graphical user interface, with four tab pages (control, acquisition, analysis, and calibration), is described step-by-step in ???.

---

##  Getting Started

###  Installation

Build the project from source:

1. Clone the Gigapixel-Woodbot repository:
```sh
❯ git clone ??
```

2. Navigate to the project directory:
```sh
❯ cd Gigapixel-Woodbot
```

3. Install the required start the system with docker:
```sh
❯ docker compose up
```

Docker will begin pulling the images, and once the process is complete, it will start the system.

###  Usage

To run the project, execute the following command in the repository folder:

```sh
❯ docker compose up
```

---

## Cite our work

You can find the paper where the model is discribed [here](http://google.com), our cite our work with the following bibtex snippet:

```tex
TODO
```

---

##  License

TODO: This project is protected under the [SELECT-A-LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

