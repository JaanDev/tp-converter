# tp-converter
A small script to convert texture packs to medium and low quality.

## Author
Jaan#2897

## Usage
This converter supports both .plist and .fnt files. It also downscales the image with the plist or fnt.

You can use it like<br>
`python converter.py -i "your highest quality file path`
<br>And it will automatically convert it one quality lower (uhd -> hd; hd -> low)

However, you can do<br>
`python converter.py -i "your highest quality file path" -a`
<br>Which will convert it to every quality possible at once without having to rerun (uhd -> hd -> low; hd -> low)

## Special Thanks
* Italian Apk Downloader for his original script
