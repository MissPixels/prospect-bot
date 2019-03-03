# Pröspect image bot

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

This is the images processing bot behind [Pröspect](https://pröspect.art), an art project that reassembles images from [McCord Museum](https://www.musee-mccord.qc.ca)'s photo collection.

The bot consists in a Flask API relying on a few libraries to process images:

- [Google's Cloud Vision API](https://cloud.google.com/vision/) is used to find images similar to the one that is being processed
- [OpenCV](https://opencv.org/) is used to extract and colorize features in the original image.
- [pixelsort](https://github.com/satyarth/pixelsort) is used to create a pixel-sorted version of the original image
- [Pillow](https://pillow.readthedocs.io/) is responsible for assembling and saving the final image
- [pytracery](https://github.com/aparrish/pytracery) generates random poems by picking verses in the [text_rules.json](./text_rules.json) file

## Example

Here's an example of each processing step.

### Original image

First, an image is picked randomly in the museum's collection.

![Original image](https://i.imgur.com/XrDbllJ.jpg)

### Modified images

Then we generate a few modified vesions of the image:

1. We use OpenCV's grabCut method to extract the image's background and replace it with the current color
2. OpenCV's contours method let's us draw some features in the image, again using the current color. This image is also used to find similar images.
3. The third image is the pixel-sorted version

![GrabCut image](https://i.imgur.com/p2vKvtY.jpg)
![Contours image](https://i.imgur.com/NBdjuuV.jpg)
![Pixelsort image](https://i.imgur.com/TmyUfOw.jpg)

### Final image

We then compose the final image by taking a slice of each version of the image, as well as a slice of 5 visually similar images found with Google's Cloud Vision API.

![Final image](https://i.imgur.com/FIxoqb3.jpg)


## Requirements

- Python >=3.6.5
- OpenCV-Python
- pixelsort
- MongoDB

## Install

```sh
$ python -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ apt-get install python-opencv
```

## Setup

- Make sure you have an Vision API-authorized GCP service account key saved as `./service-account.json`.
- Clone pixelsort in the project's root:

```sh
git clone https://github.com/satyarth/pixelsort.git
```
- Create a `.env` file based on the example file and set environment variables as needed

```sh
cp .env.example .env
```

## Run in development

Start Flask app in debug mode.

```sh
$ ./dev
```

## Run in production

Start Flask app with gunicorn.

```sh
$ ./prod
```

## Freeze requirements

```sh
$ pip freeze > requirements.txt
```

## Cleanup intermediary image files

```sh
$ rm static/(colorized|pixelsorted)/*.png
```

## Usage

Once you have the bot up and running, process images by calling the `/process-image` endpoint with the `image_url` GET parameter, ie:

```
http://127.0.0.1:5000/process-image?image_url=https://i.imgur.com/ByVWQfM.jpg
```

![Result](https://i.imgur.com/pCrr6aH.jpg)

## Credits

- **[Isabelle Gagné](http://www.isabellegagne.ca/)** - multimedia artist
- **[Paul Gascou-Vaillancourt](https://paulgv.com/)** - programmer
- **Stéphane Archambault** - author
