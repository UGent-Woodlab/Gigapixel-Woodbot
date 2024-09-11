/*
 * Created on Tue Sep 15 2023
 *
 * The MIT License (MIT)
 * Copyright (c) 2023 Simon Vansuyt UGent-Woodlab
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software
 * and associated documentation files (the "Software"), to deal in the Software without restriction,
 * including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
 * TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

var canvasSM = document.getElementById('row-scan-canvas-sm');
var canvasLG = document.getElementById('row-scan-canvas-lg');
// var canvasSM = document.getElementById('row-scan-canvas-lg');
var contextSM = canvasSM.getContext('2d');
var contextLG = canvasLG.getContext('2d');

// contextSM.strokeStyle = "black";
contextSM.strokeStyle = '#bd2130';
contextLG.strokeStyle = '#bd2130';

var cords = document.getElementsByClassName("cord");
var cord_input = [
    {
        x: document.getElementById('x_cord1'),
        y: document.getElementById('y_cord1'),
    },
    {
        x: document.getElementById('x_cord2'),
        y: document.getElementById('y_cord2'),
    }
]

var scale_factor = 10/4;

var swapCords = function() {
    if (cord_input[0].y.value < cord_input[1].y.value) {
        var copy = cord_input[0].y.value;
        cord_input[0].y.value = cord_input[1].y.value;
        cord_input[1].y.value = copy;
    }
    if (cord_input[0].x.value < cord_input[1].x.value) {
        var copy = cord_input[0].x.value;
        cord_input[0].x.value = cord_input[1].x.value;
        cord_input[1].x.value = copy;
    }
}

// calculate canvasSM offset in window
var canvasSMOffset = canvasSM.getBoundingClientRect();
var offsetX = canvasSMOffset.left;
var offsetY = canvasSMOffset.top;

var startPosition = { x: null, y: null };
var currentPosition = { x: null, y: null };
var status = 'pending';


canvasSM.addEventListener('mouseenter', function (e) {
  status = 'pending';
  canvasSM.style.cursor = 'crosshair';
});

canvasSM.addEventListener('mouseout', function (e) {
  status = 'pending';
  canvasSM.style.cursor = 'auto';
});

canvasSM.addEventListener('mousedown', function (e) {
  // start drawing
  status = 'drawing';
  startPosition = {
    x: parseInt(e.clientX - offsetX),
    y: parseInt(e.clientY - offsetY)
  };
});

canvasSM.addEventListener('mousemove', function (e) {
  if (status === 'drawing') {   
    // clear canvasSM
    contextSM.clearRect(0, 0, canvasSM.width, canvasSM.height);

    // get current mouse position
    currentPosition = {
      x: parseInt(e.clientX - offsetX),
      y: parseInt(e.clientY - offsetY)
    };
    
    // update canvasSM
    const width = currentPosition.x - startPosition.x;
    const height = currentPosition.y - startPosition.y;
    contextSM.strokeRect(startPosition.x, startPosition.y, width, height);

    cord_input[0].x.value = (startPosition.y) * scale_factor;
    cord_input[0].y.value = (startPosition.x) * scale_factor;
    cord_input[1].x.value = (startPosition.y + height) * scale_factor;
    cord_input[1].y.value = (startPosition.x + width) * scale_factor;
    // swapCords();
  }
});

canvasSM.addEventListener('mouseup', function (e) {
  // finish drawing
  if (status === 'drawing') {
    status = 'pending';
  }
});

var updateRect = function() {
    // if input changes occured change rect
    // swapCords();
    contextSM.clearRect(0, 0, canvasSM.width, canvasSM.height);
    contextSM.strokeRect(
        cord_input[0].y.value / scale_factor, 
        cord_input[0].x.value / scale_factor,
        (cord_input[1].y.value - cord_input[0].y.value) / scale_factor,
        (cord_input[1].x.value - cord_input[0].x.value) / scale_factor,
    );
};

// add evente listiner to cords input to change the rect when input changes
Array.from(cords).forEach(function(element) {
    element.addEventListener('change', updateRect);
});