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

var radio_inputs = document.getElementsByClassName('step-size-cnc');
var label_fields = document.getElementsByClassName('step-size-label');

var radio_update = (current_label) => {
    Array.from(label_fields).forEach(function(element) {
        element.classList.remove("active");
        element.firstChild.checked = false;
    });
    current_label.classList.add("active");
    current_label.firstChild.checked = true;
};

Array.from(label_fields).forEach(function(element) {
    element.addEventListener('click', () => {radio_update(element)});
});

