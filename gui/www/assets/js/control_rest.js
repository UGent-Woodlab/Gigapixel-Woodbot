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

const MAX_X = 1000
const MAX_Y =  595
const MAX_Z =  100

const CAUTION_Z = 75

// xyz speed sliders
const speed_slider = document.getElementById("speed_slider")

const speed_value = document.getElementById("speed_value")

// active acquisition interface
const alert_active_div = document.getElementById("acquisition-active-alert")
alert_active_div.classList.add("d-none")
// Caution alert
const alert_damage_div = document.getElementById("damage-danger-alert");

const disable_buttons = (status) => {
    document.querySelectorAll('button').forEach((button) => {
        button.disabled = status;
    });
};

const execute_get_rest_call = async (url) => {
    data = await fetch(url.href)
        .then(response =>{
            return response.json();
        }).then(data=>{
            return data;
        }).catch(error =>{
            console.error(error);
            disable_buttons(false);
            return {};
        });
    
    console.log(data);
    
    // axis position
    document.getElementById("x_position").innerHTML = Number(data["x"]).toFixed(2) + "&nbsp;mm";
    document.getElementById("y_position").innerHTML = Number(data["y"]).toFixed(2) + "&nbsp;mm";
    document.getElementById("z_position").innerHTML = Number(data["z"]).toFixed(2) + "&nbsp;mm";
    
    // axis speed
    document.getElementById("speed").innerHTML = data["speed"] + "&nbsp;mm/min";
    document.getElementById("speed_p").innerHTML = data["speed_p"] + "&nbsp;%";
    speed_slider.value = data["speed_p"]
    speed_value.innerHTML = data["speed_p"] + " %"

    // laser sensor
    document.getElementById("d_measure").innerHTML = data["d"] + "&nbsp;mm";
    document.getElementById("laser_value").innerHTML = data["d"] + "&nbsp;mm";

    document.getElementById("camera_name_span").innerText = data["camera_name"]

    if (data["x"] === undefined) {
        alert_active_div.classList.remove("d-none");
        disable_buttons(true);
        console.log("data is not available")
    } else {
        console.log("data is available", data)
        alert_active_div.classList.add("d-none");
        // Caution alert toggle
        if (Number(data["z"]) <= CAUTION_Z) {
            alert_damage_div.classList.add("d-none");
        } else {
            alert_damage_div.classList.remove("d-none");
        }
        disable_buttons(data["buzy"]);
    }


};

let move_cnc = async (x=NaN, y=NaN, z=NaN) => {
    let cnc_url = new URL(acquisition_url.href + "cnc/move");

    console.log(x, y, z)
    if (!Number.isNaN(parseFloat(x))) {
        cnc_url.searchParams.append('x', x);
    }
    if (!Number.isNaN(parseFloat(y))) {
        cnc_url.searchParams.append('y', y);
    }
    if (!Number.isNaN(parseFloat(z))) {
        cnc_url.searchParams.append('z', z);
    }
    console.log(cnc_url.href)

    disable_buttons(true);
    return execute_get_rest_call(cnc_url);
}

let move_cnc_relative = async (x=NaN, y=NaN, z=NaN) => {
    let cnc_url = new URL(acquisition_url.href + "cnc/move_relative");

    console.log(x, y, z)
    if (!Number.isNaN(parseFloat(x))) {
        cnc_url.searchParams.append('x', x);
    }
    if (!Number.isNaN(parseFloat(y))) {
        cnc_url.searchParams.append('y', y);
    }
    if (!Number.isNaN(parseFloat(z))) {
        cnc_url.searchParams.append('z', z);
    }
    console.log(cnc_url.href)

    disable_buttons(true);
    return execute_get_rest_call(cnc_url);
}

let set_speed = async (p) => {
    let cnc_url = new URL(acquisition_url.href + "cnc/set_speed");

    cnc_url.searchParams.append('p', p);

    disable_buttons(true);
    return execute_get_rest_call(cnc_url);
}

const send_gcode = async (gocde) => {
    let cnc_url = new URL(acquisition_url.href + "cnc/gcode");
    cnc_url.searchParams.append('gcode', gcode);
    disable_buttons(true);
    return execute_get_rest_call(cnc_url);
}


// get init config of page
setInterval(() => {execute_get_rest_call(acquisition_url)}, 500);

// -- Move machine control -- 
// home
const home_button = document.getElementById("home");
home_button.addEventListener("click", () => {move_cnc(0, 0, 0)});

// max X 
const x_max_button = document.getElementById("x_max");
x_max_button.addEventListener("click", () => {move_cnc(MAX_X)});

// max Y
const y_max_button = document.getElementById("y_max");
y_max_button.addEventListener("click", () => {move_cnc(NaN, MAX_Y)});

// max Z
const z_max_button = document.getElementById("z_max");
z_max_button.addEventListener("click", () => {move_cnc(NaN, NaN, MAX_Z)});

// Get input and send coordinates
const go_cords_button = document.getElementById("move_cords");
go_cords_button.addEventListener("click", () => {
    const x_cord = document.getElementById("move_cords_x_input").value;
    const y_cord = document.getElementById("move_cords_y_input").value;
    const z_cord = document.getElementById("move_cords_z_input").value;
    move_cnc(x_cord, y_cord, z_cord);
});

// -- Axis Control --
// fetch selected step size
let step = () => {
    return parseFloat(document.getElementById("step_size_group").querySelector(".active").querySelector("input").value);
};

// XY Axis
const left_step_button = document.getElementById("left_step_button");
left_step_button.addEventListener("click", () => {move_cnc_relative(-step())});
const right_step_button = document.getElementById("right_step_button");
right_step_button.addEventListener("click", () => {move_cnc_relative(step())});

const down_step_button = document.getElementById("down_step_button");
down_step_button.addEventListener("click", () => {move_cnc_relative(NaN, -step())});
const up_step_button = document.getElementById("up_step_button");
up_step_button.addEventListener("click", () => {move_cnc_relative(NaN, step())});

// Z Axis
const z_down_step_button = document.getElementById("z_down_step_button");
z_down_step_button.addEventListener("click", () => {move_cnc_relative(NaN, NaN, -step())});
const z_up_step_button = document.getElementById("z_up_step_button");
z_up_step_button.addEventListener("click", () => {move_cnc_relative(NaN, NaN, step())});


// -- Set speed control --
speed_slider.addEventListener("change", () => {
    speed_value.innerHTML = speed_slider.value + "%";
    set_speed(parseInt(speed_slider.value));
});

const speed_down_button = document.getElementById("down_speed");
speed_down_button.addEventListener("click", () => {
    set_speed(parseInt(speed_slider.value)-1);
    console.log(speed_slider.value)
});

const speed_up_button = document.getElementById("up_speed");
speed_up_button.addEventListener("click", () => {
    set_speed(parseInt(speed_slider.value)+1);
    console.log(speed_slider.value)
});

// 
const gcode_send_button = document.getElementById("gcode_send_button");
gcode_send_button.addEventListener("click", () => {
    gcode = document.getElementById("gcode_input").value;
    send_gcode(gcode);
});

// camera control
const update_view = document.getElementById("update_view");
update_view.addEventListener("click", () => {
    const url = new URL(acquisition_url.href + "camera/update_current");
    execute_get_rest_call(url);
    setTimeout(() => {
        let d = new Date();
        let img_html = '<img style="width: 1024; height: 1024;" src="http://localhost:5000/camera/current_view.jpg?time=' + d.getTime() + '" width="600px">';
        document.getElementById("current_view_image").innerHTML = img_html
    }, 3500);
});

const download_view = document.getElementById("download_view");
download_view.addEventListener("click", () => {
    const url = new URL(acquisition_url.href + "camera/download_view");
    execute_get_rest_call(url);
});


// laser control
const camera_to_laser_button = document.getElementById("camera_to_laser");
camera_to_laser_button.addEventListener("click", () => {
    const url = new URL(acquisition_url.href + "laser/camera_to_laser");
    execute_get_rest_call(url);
});
