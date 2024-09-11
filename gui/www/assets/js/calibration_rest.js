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

// hard coded variables
const acquisition_url = new URL("http://127.0.0.1:5000");


const execute_get_rest_call = async (url) => {
    data = await fetch(url.href)
        .then(response =>{
            console.log("raw response", response);
            return response.json();
        }).then(data=>{
            return data;
        }).catch(error =>{
            console.error(error);
            return {};
        });
    
    console.log(data);
    return data;
};

const fetch_settings = async () => {
    const url = new URL(acquisition_url.href + "calibration/get_current_setting");
    data = await execute_get_rest_call(url);
    // axis position
    document.getElementById("x_position").innerHTML = data["x"] + " mm";
    document.getElementById("y_position").innerHTML = data["y"] + " mm";
    document.getElementById("z_position").innerHTML = data["z"] + " mm";

    document.getElementById("camera_name_a").innerHTML = data["camera_name"];
};

fetch_settings();

const x_laser_to_camera = document.getElementById("x_laser_to_camera")
const x_laser_to_camera_button = document.getElementById("x_laser_to_camera_button")

x_laser_to_camera_button.addEventListener("click", () => {
    const update_url = new URL(acquisition_url.href + "calibration/update_settings");
    update_url.searchParams.append("laser_to_camera_x", x_laser_to_camera.value)

    execute_get_rest_call(update_url);
    fetch_settings();
});

const y_laser_to_camera = document.getElementById("y_laser_to_camera")
const y_laser_to_camera_button = document.getElementById("y_laser_to_camera_button")

y_laser_to_camera_button.addEventListener("click", () => {
    const update_url = new URL(acquisition_url.href + "calibration/update_settings");
    update_url.searchParams.append("laser_to_camera_y", y_laser_to_camera.value)
    
    execute_get_rest_call(update_url);
    fetch_settings();
});

const z_laser_to_camera = document.getElementById("z_laser_to_camera")
const z_laser_to_camera_button = document.getElementById("z_laser_to_camera_button")

z_laser_to_camera_button.addEventListener("click", () => {
    const update_url = new URL(acquisition_url.href + "calibration/update_settings");
    update_url.searchParams.append("laser_to_camera_z", z_laser_to_camera.value)

    execute_get_rest_call(update_url);
    fetch_settings();
});


// swap cordiantes
const update_xy_manual_button = document.getElementById("update_xy_manual_button");
const x_change_manual = document.getElementById("x_change_manual");
const y_change_manual = document.getElementById("y_change_manual");

const x_new = document.getElementById("x-new");
const y_new = document.getElementById("y-new");

update_xy_manual_button.addEventListener("click", async () => {
    const x = x_change_manual.value;
    const y = y_change_manual.value;
    console.log(x, y)

    const url = new URL(acquisition_url.href + "calibration/manual_xy");
    url.searchParams.append("x", x);
    url.searchParams.append("y", y);

    data = await execute_get_rest_call(url);

    // update image
    let d = new Date();
    // const img_html = '<img style="width: 1024;height: 1024;" src="http://localhost:5000/camera/current_view.jpg?time=' + d.getTime() + '" width="500">';
    const img_html = '<img id="manual_xy_img" src="http://localhost:5000/calibration/manual_xy_picture.png?time=' + d.getTime() + '" width="500px" />'
    document.getElementById("manual_xy_container").innerHTML = img_html;
    // setTimeout(() => {
    // }, 3500);

    // update lower span
    x_new.innerHTML = data["x"];
    y_new.innerHTML = data["y"];
});

const confirm_update_button = document.getElementById("confirm_update");
confirm_update_button.addEventListener("click", () => {
    const x = x_new.innerHTML;
    const y = y_new.innerHTML;

    const update_url = new URL(acquisition_url.href + "calibration/update_settings");
    update_url.searchParams.append("laser_to_camera_x", x);
    update_url.searchParams.append("laser_to_camera_y", y);

    execute_get_rest_call(update_url);
    fetch_settings();
});

const z_start = document.getElementById("z_start");
const z_step = document.getElementById("z_step");
const amount = document.getElementById("amount");
const take_z_button = document.getElementById("take_z_button");

const carousel_container = document.getElementById("carousel-container");
// const carousel_ol = document.getElementById("carousel-ol");
const carousel_select = document.getElementById("carousel-select");

take_z_button.addEventListener("click", async () => {
    const url = new URL(acquisition_url.href + "/calibration/take_z_stack");
    // /calibration/get_stack_by_index

    url.searchParams.append("z_start", z_start.value);
    url.searchParams.append("step", z_step.value);
    url.searchParams.append("amount", amount.value);

    data = await execute_get_rest_call(url);

    carousel_container.innerHTML = '';
    carousel_select.innerHTML = '';

    for (let i=0; i<data["result"].length; i++) {
        const carousel_item = (
            `<div class="carousel-item ` + (i==0?`active">`:`">`) +
                `<h5>index ${i} with z=${data["result"][i]["h"]}</h5><img class="w-100 d-block w-100" src="http://localhost:5000/calibration/get_stack_by_index?file_name=${data["result"][i]["file_name_png"]}" width="500px" />` +
            `</div>`
        )
        carousel_container.innerHTML += carousel_item;

        const carousel_options = (
            `<option value="${data["result"][i]["h"]}" ` + (i==0?`selected`:``) + ` >${i}</option>`
        )
        carousel_select.innerHTML += carousel_options
    }

    carousel_container.insertAdjacentHTML('afterend', `<img class="w-100 d-block w-100" src="http://localhost:5000/calibration/get_stack_by_index?file_name=${data["var_of_laplacian_path"]}" width="650px" /><h7>Suggestion for best index is ${data["best_index"]}</h7>`);
});

const update_z_setting_button = document.getElementById("update_z_setting_button");
const select_index_z = document.getElementById("select_index_z");

update_z_setting_button.addEventListener("click", () => {
    const update_url = new URL(acquisition_url.href + "calibration/update_settings");
    update_url.searchParams.append("laser_to_camera_z", select_index_z.value);

    execute_get_rest_call(update_url);
    fetch_settings();
});
