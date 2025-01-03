// new_template.js
window.onload = function () {
    'use strict';
  
    var Cropper = window.Cropper;
    var image = document.getElementById('image');
    var cropButton = document.getElementById('crop-button');
    var options = {
      aspectRatio: NaN, // Default aspect ratio for cropping
      preview: '.img-preview', // Preview container
      viewMode: 1, // Restrict the crop box to stay within the canvas
      zoomOnWheel: true, // Enable zooming with the mouse wheel
      scalable: true, // Allow scaling of the image
      movable: true, // Allow moving the image
      autoCropArea: 0.5, // Set initial cropping area
      cropBoxMovable: true, // Enable dragging the crop box
      cropBoxResizable: true, // Enable resizing the crop box
      ready: function () {
        console.log('Cropper is ready.');
      },
    };
  
    var cropper = new Cropper(image, options);
  
    // Handle cropping action
    cropButton.addEventListener('click', function () {
      var croppedCanvas = cropper.getCroppedCanvas();
  
      if (croppedCanvas) {
        var croppedImage = document.getElementById('cropped-result');
        croppedImage.innerHTML = '';
        croppedImage.appendChild(croppedCanvas);
      }
    });
  };
  