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

const acquisition_queue = document.getElementById("acquisition_queue")

update_queue = async () => {
    const url = new URL(acquisition_url.href + "acquisition/acquisition_queue");
    const data = await execute_get_rest_call(url);
    const settings_data = await execute_get_rest_call(acquisition_url);

    document.getElementById("camera_name_span").innerText = settings_data["camera_name"];

    if (!data["thread_is_active"]) {
        // nothing happening
        const tr =  (
            `<tr class="border-1 border rounded-0">` + 
                `<td class="text-center border rounded-0" colspan="7"><span><span style="color: var(--bs-gray-600); background-color: rgba(68,70,84,var(--tw-bg-opacity));">Currently, there are no ongoing acquisition jobs. </br> Create a job to have it displayed on this table.</span></span></td>` +
            `</tr>`
        )

        acquisition_queue.innerHTML = tr

    } else if (data["queue"].length == 0 && data["current_task"] == null) {
        console.log(data["current_task"])
        // add failure to the table
        acquisition_queue.innerHTML = ""

        const tr_error =  (
            `<tr class="border-1 border rounded-0" table-warning>` + 
                `<td class="text-center border rounded-0" colspan="7"><span><span style="color: var(--bs-gray-600); background-color: rgba(68,70,84,var(--tw-bg-opacity));"> Acquisition consumer isn't active at te moment.<br/> Something most have gone wrong.</span></span></td>` +
            `</tr>`
        )

        acquisition_queue.innerHTML = tr_error

        const tr = (
            `<tr class="border rounded-0 table-danger">` +
                `<td class="border rounded-0">${data["current_task"]["name"]}</td>` + 
                `<td class="border rounded-0" style="text-align: center;">${data["current_task"]["date"]}</td>` +
                `<td class="text-center border rounded-0" style="text-align: center;">${data["current_task"]["x_cord1"]} mm</td>` +
                `<td class="text-center border rounded-0" style="text-align: right;">${data["current_task"]["y_cord1"]} mm</td>` +
                `<td class="text-center border rounded-0" style="text-align: right;">${data["current_task"]["x_cord2"]} mm</td>` +
                `<td class="text-center border rounded-0" style="text-align: right;">${data["current_task"]["y_cord2"]} mm</td>` +
                `<td class="text-center border rounded-0" style="text-align: right;">${data["current_task"]["picture_overlap"]} %</td>` +
            `</tr>`
        )

        acquisition_queue.innerHTML += tr
    } else {
        // add current job in blue to the queue table
        acquisition_queue.innerHTML = ""

        const tr = (
            `<tr class="border rounded-0 table-primary">` +
                `<td class="border rounded-0">${data["current_task"]["name"]}</td>` + 
                `<td class="border rounded-0" style="text-align: center;">${data["current_task"]["date"]}</td>` +
                `<td class="text-center border rounded-0" style="text-align: center;">${data["current_task"]["x_cord1"]} mm</td>` +
                `<td class="text-center border rounded-0" style="text-align: right;">${data["current_task"]["y_cord1"]} mm</td>` +
                `<td class="text-center border rounded-0" style="text-align: right;">${data["current_task"]["x_cord2"]} mm</td>` +
                `<td class="text-center border rounded-0" style="text-align: right;">${data["current_task"]["y_cord2"]} mm</td>` +
                `<td class="text-center border rounded-0" style="text-align: right;">${data["current_task"]["picture_overlap"]} %</td>` +
            `</tr>`
        )

        acquisition_queue.innerHTML += tr
    
    }

    // add the other jobs to the queue table
    for (let i=0; i<data["queue"].length; i++) {
        const row = data["queue"][i]
        console.log("row", row)
        const tr = (
            `<tr class="border rounded-0">` +
                `<td class="border rounded-0">${row["name"]}</td>` +
                `<td class="border rounded-0" style="text-align: center;">${row["date"]}</td>` +
                `<td class="text-center border rounded-0" style="text-align: center;">${row["x_cord1"]} mm</td>` +
                `<td class="text-center border rounded-0" style="text-align: right;">${row["y_cord1"]} mm</td>` +
                `<td class="text-center border rounded-0" style="text-align: right;">${row["x_cord2"]} mm</td>` +
                `<td class="text-center border rounded-0" style="text-align: right;">${row["y_cord2"]} mm</td>` +
                `<td class="text-center border rounded-0" style="text-align: right;">${row["picture_overlap"]} %</td>` +
            `</tr>`
        )
        console.log("tr", tr)
        acquisition_queue.innerHTML += tr
    }
}

// start base_scan
const base_scan_work_area_input = document.getElementById("base_scan_work_area_input");
const base_scan_z_input = document.getElementById("base_scan_z_input");
const start_base_scan_button = document.getElementById("base_scan_button");
const base_scan_step_input = document.getElementById("base_scan_step_input");
base_scan_button.addEventListener("click", async () => {
    const url = new URL(acquisition_url.href + "acquisition/base_scan");

    url.searchParams.append("percentage", base_scan_work_area_input.value);
    url.searchParams.append("z_height", base_scan_z_input.value);
    url.searchParams.append("step_size", base_scan_step_input.value);

    await execute_get_rest_call(url);
    document.getElementById("workspace").style.backgroundImage = "url(http://127.0.0.1:5000/acquisition/base_scan.png)"
})

// start basic job
const x_cord1 = document.getElementById("x_cord1");
const y_cord1 = document.getElementById("y_cord1");
const x_cord2 = document.getElementById("x_cord2");
const y_cord2 = document.getElementById("y_cord2");

const get_export_jobs = async () => {
    const url = new URL(acquisition_url.href + "acquisition/export_job_file");
    acquisition_jobs = await execute_get_rest_call(url)

    $("#task-to-export").empty()
    if (acquisition_jobs.length == 0) {
        $("#task-to-export").append(
            `<li class="list-group-item">
                Here you can see all the jobs task to export.  
            </li>`
        )
    } else {
        $("#task-to-export").append(
            `<li class="list-group-item">
                <div class="row justify-content-center" style="text-align:center;">
                    <div class="col"><strong>Name</strong></div>
                    <div class="col"><strong>Type</strong></div>
                    <div class="col"><strong>(X1, Y1)</strong></div>
                    <div class="col"><strong>(X2, Y2)</strong></div>
                    <div class="col"></div>
                </div>
            </li>`
        )
        for (const job of acquisition_jobs) {
            $("#task-to-export").append(
                `<li class="list-group-item">
                    <div class="row justify-content-center" style="text-align:center;">
                        <div class="col" style="padding-top:6px;text-align:center;">${job["name"]}</div>
                        <div class="col" style="padding-top:6px;text-align:center;">${job["type"]}</div>
                        <div class="col" style="padding-top:6px;text-align:center;">(${job["x_cord1"]}, ${job["y_cord1"]})</div>
                        <div class="col" style="padding-top:6px;text-align:center;">(${job["x_cord2"]}, ${job["y_cord2"]})</div>
                        <div class="col">
                            <button id="delete-${job["name"]}-button" class="btn btn-danger" type="button"><i class="inline-icon material-icons">&#xe872;</i></button>
                        </div>
                    </div>
                </li>`
            )

            document.getElementById(`delete-${job["name"]}-button`).addEventListener("click", async (e) => {
                const url = new URL(acquisition_url.href + "/acquisition/remove_item_from_export");
                url.searchParams.append("name", job["name"]);
                await execute_get_rest_call(url);
                update_queue();
            });
        }
    }
}


const download_export_job_file_button = document.getElementById("download_export_job_file_button");
download_export_job_file_button.addEventListener("click", async () => {
    console.log("yay pressed button")
    const url = new URL(acquisition_url.href + "acquisition/export_job_file");
    acquisition_jobs = await execute_get_rest_call(url)
    
    var element = document.createElement('a');
    element.style.display = 'none';
    element.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(JSON.stringify(acquisition_jobs, undefined, 2)));
    element.setAttribute("download", "acquisiton_jobs.json");
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    console.log("yay pressed button->done")
});

const name_input_object = document.getElementById("name_input_object");
const height_z_object = document.getElementById("height_z_object");
const height_step_object = document.getElementById("height_step_object");
const height_threshold_object = document.getElementById("height_threshold_object");
const margin_object = document.getElementById("margin_object");
const picture_overlap_object = document.getElementById("picture_overlap_object");

const start_object_acq_button = document.getElementById("start_object_acq");
const add_object_acq_button = document.getElementById("add_object_acq");

const start_object_acq = (to_export) => {
    const url = new URL(acquisition_url.href + "acquisition/object");

    url.searchParams.append("x_cord1", x_cord1.value);
    url.searchParams.append("y_cord1", y_cord1.value);
    url.searchParams.append("x_cord2", x_cord2.value);
    url.searchParams.append("y_cord2", y_cord2.value);

    url.searchParams.append("name", name_input_object.value);
    url.searchParams.append("height_z", height_z_object.value);
    url.searchParams.append("height_step", height_step_object.value);
    url.searchParams.append("height_threshold", height_threshold_object.value);
    url.searchParams.append("margin", margin_object.value);
    url.searchParams.append("picture_overlap", picture_overlap_object.value);
    url.searchParams.append("to_export", to_export);

    execute_get_rest_call(url);
    update_queue();
}

start_object_acq_button.addEventListener("click", () => {start_object_acq(false)});
add_object_acq_button.addEventListener("click", () => {
    start_object_acq(true);
    get_export_jobs();
});

// check drill sample objects
const amount_of_drill_input = document.getElementById("amount_of_drill_input");
const names_container = document.getElementById("names");

const height_z_drill = document.getElementById("height_z_drill");
const picture_overlap_drill = document.getElementById("picture_overlap_drill");

amount_of_drill_input.addEventListener("change", () => {
    // console.log(amount_of_drill_input.value)
    names_container.innerHTML = ""
    const amount = parseInt(amount_of_drill_input.value)
    for (let i=1; i<amount+1; i++) {
        console.log(i)
        const html_row = `<div class="col"><div class="input-group"><span class="input-group-text input-group-text">Sample ${i}:</span><input class="form-control form-control" id="name_${i}" type="text" placeholder="MF_8N"></div></div>`
        names_container.innerHTML += html_row
    }
})

const add_drill_acq_button = document.getElementById("add_drill_acq_button");
const start_drill_acq_button = document.getElementById("start_drill_acq_button");

const start_drill_sample_acq = (to_export) => {
    // fetch the names of the drill samples
    let names = []

    const amount = parseInt(amount_of_drill_input.value);

    for (let i=1; i<amount+1; i++) {
        const name = document.getElementById(`name_${i}`).value;
        names.push(name)
    }

    const url = new URL(acquisition_url.href + "acquisition/drill_sample");
    // append parameters to url
    url.searchParams.append("x_cord1", x_cord1.value);
    url.searchParams.append("y_cord1", y_cord1.value);
    url.searchParams.append("x_cord2", x_cord2.value);
    url.searchParams.append("y_cord2", y_cord2.value);

    url.searchParams.append("name", names);
    url.searchParams.append("height_z", height_z_drill.value);
    url.searchParams.append("picture_overlap", picture_overlap_drill.value);
    url.searchParams.append("to_export", to_export);

    // execute job
    execute_get_rest_call(url);
    update_queue();
}

start_drill_acq_button.addEventListener("click", () => {start_drill_sample_acq(false)});
add_drill_acq_button.addEventListener("click", () => {
    start_drill_sample_acq(true);
    get_export_jobs();
});

// object fixed z axis acquisition
const name_input_object_fixed = document.getElementById("name_input_object_fixed");
const fixed_z_start = document.getElementById("fixed_z_start");
const fixed_z_amount = document.getElementById("fixed_z_amount");
const fixed_z_step = document.getElementById("fixed_z_step");
const picture_overlap_object_fixed = document.getElementById("picture_overlap_object_fixed");

const start_object_fixed_acq = document.getElementById("start_object_fixed_acq");
const add_object_fixed_acq = document.getElementById("add_object_fixed_acq");

const start_object_fixed_task = (to_export) => {
    const url = new URL(acquisition_url.href + "acquisition/object_fixed");

    url.searchParams.append("x_cord1", x_cord1.value);
    url.searchParams.append("y_cord1", y_cord1.value);
    url.searchParams.append("x_cord2", x_cord2.value);
    url.searchParams.append("y_cord2", y_cord2.value);

    url.searchParams.append("name", name_input_object_fixed.value);
    url.searchParams.append("z_start", fixed_z_start.value);
    url.searchParams.append("z_amount", fixed_z_amount.value);
    url.searchParams.append("z_step", fixed_z_step.value);
    url.searchParams.append("picture_overlap", picture_overlap_object_fixed.value);
    url.searchParams.append("to_export", to_export);

    execute_get_rest_call(url);
    update_queue();
}

start_object_fixed_acq.addEventListener("click", () => {start_object_fixed_task(false)});
add_object_fixed_acq.addEventListener("click", () => {
    start_object_fixed_task(true);
    get_export_jobs();
});

// Load acquisition tasks from json file
const acquisition_file_input = document.getElementById("acquisition-file-input")
acquisition_file_input.addEventListener("change", (e) => {
    console.log(e.target.files[0]);

    $("#import-from-file-modal").empty().append(`File ${e.target.files[0]["name"]}`)
    $("#import-from-file").modal("show")

    var reader = new FileReader()
    reader.readAsText(e.target.files[0], "UTF-8")


    reader.addEventListener("load", (evt) => {
        try {
            json_file = JSON.parse(evt.target.result);
            $("#start-acq-from-file-button").prop("disabled", false);
        } catch(error) {
            $("#file-import-code").empty().html(`${error}`);
            $("#start-acq-from-file-button").prop("disabled", true);
            return;
        }
        const url = new URL(acquisition_url.href + "acquisition/import_from_file");
        url.searchParams.append("body", JSON.stringify(json_file));

        $("#file-import-code").empty().html(JSON.stringify(json_file, null, 2).replace(/\n( *)/g, function (match, p1) {
            return '<br>' + '&nbsp;'.repeat(p1.length);
        }));

        // remove all previous events on the start button
        $("#start-acq-from-file-button").replaceWith($("#start-acq-from-file-button").clone());
        // add new event that exectues the tasks
        $("#start-acq-from-file-button").click(() => {
            execute_get_rest_call(url);
            update_queue();
            $("#import-from-file").modal("close");
        });
    });
    // fetch(e.target.files[0])
    //     .then(resp => resp.json())
    //     .then(data => console.log(data))
});

update_queue();
get_export_jobs();
setInterval(update_queue, 1500);
setInterval(get_export_jobs, 1500);
