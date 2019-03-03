import os
import re
from flask import Flask, request, Response, jsonify, safe_join
from flask_cors import CORS
from bson import json_util
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from app.utils.helpers import getConfig, getFilePath, nl2br, isAuthorizedRequest
from app.ImageSearcher import ImageSearcher
from app.ColorPicker import ColorPicker
from app.ImageProcessor import ImageProcessor
from app.Poet import Poet
from app.Tweeter import Tweeter
from app.Model import Model


def create_app():

    sentryDsn = os.getenv("SENTRY_DSN", None)
    if sentryDsn is not None:
        sentry_sdk.init(dsn=sentryDsn, integrations=[FlaskIntegration()])

    app = Flask(__name__)
    CORS(app)
    config = getConfig()
    imageSearcher = ImageSearcher()
    colorPicker = ColorPicker()
    poet = Poet()
    tweeter = Tweeter()
    model = Model()

    @app.route("/health")
    def health():
        return Response("OK", status=200)

    @app.route("/")
    @app.route("/similar-images")
    def similarImages():
        imageUrl = request.args.get("image_url")
        if imageUrl is None:
            return Response("image_url parameter is required", status=400)
        else:
            images = imageSearcher.searchWithUrl(imageUrl)
            return jsonify(images)

    @app.route("/current-color")
    def currentColor():
        color = colorPicker.getCurrentColorRgb()
        html = """
            <body
                style="
                background-color: rgb({}, {}, {});">
            </body>
        """.format(
            *color
        )
        return Response(html, status=200)

    def pickImage():
        from app.ImagePicker.ImagePicker import ImagePicker

        source = request.args.get("source")

        def imageIsUnique(url):
            return model.getCount({"url": url}) == 0
        image = ImagePicker().pickImage(source, unique=imageIsUnique)
        return image

    @app.route("/pick-image")
    def pickImageView():
        image = pickImage()
        response = app.response_class(
            response=json_util.dumps(image), status=200, mimetype="application/json"
        )
        return response

    @app.route("/generate-poem")
    def generatePoem():
        return poet.makePoem()

    @app.route("/all")
    def all():
        response = app.response_class(
            response=json_util.dumps(model.getAll()),
            status=200,
            mimetype="application/json",
        )
        return response

    @app.route("/list")
    def list():
        response = app.response_class(
            response=json_util.dumps(
                model.getPage(
                    request.args.get("page"),
                    request.args.get("size"),
                    request.args.get("fetchNext"),
                )
            ),
            status=200,
            mimetype="application/json",
        )
        return response

    @app.route("/last")
    def last():
        response = app.response_class(
            response=json_util.dumps(model.getLast()),
            status=200,
            mimetype="application/json",
        )
        return response

    @app.route("/one/<slug>")
    def one(slug):
        response = app.response_class(
            response=json_util.dumps(model.getOneBySlug(slug)),
            status=200,
            mimetype="application/json",
        )
        return response

    @app.route("/process-image")
    def processImage():
        image = {"source": None, "url": request.args.get("image_url")}
        if image["url"] is None:
            image = pickImage()
        imageProcessor = ImageProcessor()
        currentColor = colorPicker.getCurrentColorRgb()
        visuallySimilarToOriginal = imageSearcher.searchWithUrl(image["url"])
        originalImageFile, grabCutFile, countoursFile = imageProcessor.colorizeImage(
            imageUrl=image["url"], currentColor=currentColor
        )
        originalFileFullPath = getFilePath(
            originalImageFile, path=config["Files"]["OriginalImagePath"]
        )
        grabCutFilePath = getFilePath(
            grabCutFile, path=config["Files"]["ColorizedImagePath"], withRoot=False
        )
        grabCutFileFullPath = getFilePath(
            grabCutFile, path=config["Files"]["ColorizedImagePath"]
        )
        countoursFilePath = getFilePath(
            countoursFile, path=config["Files"]["ColorizedImagePath"], withRoot=False
        )
        countoursFileFullPath = getFilePath(
            countoursFile, path=config["Files"]["ColorizedImagePath"]
        )
        pixelSortedFile = imageProcessor.pixelSortImage(originalFileFullPath)
        pixelSortedFilePath = getFilePath(
            pixelSortedFile,
            path=config["Files"]["PixelSortedImagePath"],
            withRoot=False,
        )
        pixelSortedFileFullPath = getFilePath(
            pixelSortedFile, path=config["Files"]["PixelSortedImagePath"]
        )
        visuallySimilarToProcessed = imageSearcher.searchWithLocalFile(
            countoursFileFullPath
        )
        visuallySimilarImages = visuallySimilarToProcessed + visuallySimilarToOriginal
        visuallySimilarImagesLinks = [image["link"] for image in visuallySimilarImages]
        finalImage = imageProcessor.makeSlicedImage(
            [countoursFileFullPath],
            canvasImgPath=grabCutFileFullPath,
            sliceName="contours",
            minProp=0.15,
            maxProp=0.25,
        )
        finalImage = imageProcessor.makeSlicedImage(
            [pixelSortedFileFullPath],
            canvas=finalImage,
            sliceName="pixelsort",
            minProp=0.15,
            maxProp=0.25,
        )
        finalImage = imageProcessor.makeSlicedImage(
            visuallySimilarImagesLinks,
            canvas=finalImage,
            sliceName="visually similar large",
            minProp=0.10,
            maxProp=0.12,
        )
        visuallySimilarImagesLinks.pop(0)
        finalImage = imageProcessor.makeSlicedImage(
            visuallySimilarImagesLinks,
            canvas=finalImage,
            sliceName="visually similar normal",
            returnCanvas=False,
            filenamePrefix="Prospect-{}-".format(image["source"]),
            maxSlicesCount=3,
        )
        finalImageFilePath = getFilePath(
            finalImage, path=config["Files"]["FinalImagePath"], withRoot=False
        )
        finalImageFilePathFullPath = getFilePath(
            finalImage, path=config["Files"]["FinalImagePath"]
        ) + "/full.jpg"
        poem = generatePoem()

        # Persist to DB if request is authenticated
        if isAuthorizedRequest(request):
            model.insert(
                {
                    "originalUrl": image["url"],
                    "finalImagePath": finalImageFilePath + "/",
                    "gisement": image["sourceId"],
                    "description": image["description"],
                    "poem": poem,
                    "color": currentColor,
                    "slug": "{}-{}".format(
                        image["sourceId"], re.sub(r"[^0-9]", "", finalImageFilePath)
                    ),
                    "active": True,
                }
            )
            tweeter.tweet(
                poem, finalImageFilePathFullPath, additionalText=image["twitterText"]
            )
            return Response("OK", status=200)

        html = "<div>{}</div>".format(image["url"])
        html += """
            <img src="{}" />
        """.format(
            safe_join(config["Files"]["Root"], grabCutFilePath)
        )
        html += """
            <img src="{}" />
        """.format(
            safe_join(config["Files"]["Root"], countoursFilePath)
        )
        html += """
            <img src="{}" />
        """.format(
            safe_join(config["Files"]["Root"], pixelSortedFilePath)
        )
        html += """
            <img src="{}" />
        """.format(
            safe_join(config["Files"]["Root"], finalImageFilePath + "/full.jpg")
        )
        html += """
            <div>{}</div>
        """.format(
            nl2br(poem)
        )
        html += "<h1>Visually similar</h1>"
        for link in visuallySimilarImagesLinks:
            html += """
                <img src="{}" />
            """.format(
                link
            )
        return Response(html, status=200)

    return app


app = create_app()
