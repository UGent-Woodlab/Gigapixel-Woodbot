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
const analyse_url = new URL("http://127.0.0.1:5002");

const body = document.querySelector("body");

const execute_get_rest_call = async (url) => {
    data = await fetch(url.href)
        .then(response =>{
            return response.json();
        }).then(data=>{
            return data;
        }).catch(error =>{
            console.error(error);
            return str(error);
        });
    
    return data;
};

const images_list = document.getElementById("images_list");

const success_str = "Done✅"
const busy_str = "Busy⏳"
const failure_str = "Failure⛔"
const pending_str = "Pending🏴"

const start_analyse_by_date = async (date) => {
    const url = new URL(analyse_url.href + "start_by_date")
    url.searchParams.append("date", date);
    await execute_get_rest_call(url);
};

const delete_image_from_db = async (name, date) => {
    const url = new URL(analyse_url.href + "remove")
    url.searchParams.append("date", date);
    url.searchParams.append("name", name);
    await execute_get_rest_call(url);
    document.location.reload()
}

const restart_task = async (date, task_name) => {
    const url = new URL(analyse_url.href + "restart_task");
    url.searchParams.append("date", date);
    url.searchParams.append("task_type", task_name);
    await execute_get_rest_call(url);
}

const update_setting = async(date, setting_name, new_value) => {
    const url = new URL(analyse_url.href + "update_setting");
    url.searchParams.append("date", date);
    url.searchParams.append("setting_name", setting_name);
    url.searchParams.append("new_value", new_value);
    console.log(date, setting_name, new_value);
    await execute_get_rest_call(url);
}

const update_busy_tasks = async () => {
    const url = new URL(analyse_url.href + "get_busy_tasks")
    const busy_tasks = await execute_get_rest_call(url); 

    if (busy_tasks["efi_task"] != undefined) {
        const stacked_span = document.getElementById(`${busy_tasks["efi_task"]["date"]}_${busy_tasks["efi_task"]["name"]}_stacked`);
        stacked_span.innerHTML = busy_str + '<br>' +
            `(${busy_tasks["efi_task"]["finished_jobs"]}/${busy_tasks["efi_task"]["total_jobs"]}) <br>` +
            `${Math.round(parseInt(busy_tasks["efi_task"]["finished_jobs"])/parseInt(busy_tasks["efi_task"]["total_jobs"])*100)} %`;
    }
    if (busy_tasks["correction_task"] != undefined) {
        const correction_span = document.getElementById(`${busy_tasks["correction_task"]["date"]}_${busy_tasks["correction_task"]["name"]}_correction`);
        correction_span.innerHTML = busy_str + '<br>' +
            `(${busy_tasks["correction_task"]["finished_jobs"]}/${busy_tasks["correction_task"]["total_jobs"]}) <br>` +
            `${Math.round(parseInt(busy_tasks["correction_task"]["finished_jobs"])/parseInt(busy_tasks["correction_task"]["total_jobs"])*100)} %`;
    }
    if (busy_tasks["stitching_task"] != undefined) {
        const stitched_span = document.getElementById(`${busy_tasks["stitching_task"]["date"]}_${busy_tasks["stitching_task"]["name"]}_stitched`);
        stitched_span.textContent = busy_str;
    }
};

const template_modal_settings = (image) => {
    return `
    <div role="dialog" tabindex="-1" class="modal fade" id="modal-${image["date"]}" aria-hidden="true">
    <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h4 class="modal-title">Settings of ${image["name"]} (${image["date"]})</h4>
                <button class="btn-close" type="button" aria-label="Close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <h6><strong>Acquisition Info:</strong></h6>

                <table class="table">
                    <thead>
                        <tr>
                            <th scope="col">Name</th>
                            <th scope="col">Value</th>
                        </tr>
                    </thead>
                    <tbody>

                        <tr>
                            <td>Date</td>
                            <td>${image["date"]}</td>
                        </tr>
                        <tr>
                            <td>Name</td>
                            <td>${image["name"]}</td>
                        </tr>
                        <tr>
                            <td>Camera</td>
                            <td>${image["camera"]}</td>
                        </tr>
                        <tr>
                            <td>Increment (mm, mm)</td>
                            <td>(${image["increment_x"]}; ${image["increment_y"]})</td>
                        </tr>
                        <tr>
                            <td>Overlap percentage (%)</td>
                            <td>${image["overlap"]}</td>
                        </tr>
                        <tr>
                            <td>Start coordinate (mm, mm)</td>
                            <td>(${image["start_y"]}; ${image["start_x"]})</td>
                        </tr>
                        <tr>
                            <td>Path</td>
                            <td>${image["start_path"]}</td>
                        </tr>
                        <tr>
                            <td>Blending</td>
                            <td>${image["blending"]}</td>
                        </tr>

                    </tbody>
                </table>

                <h6><strong>Stitching settings:</strong></h6>
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr><th>Settting</th><th>Current value</th><th>Set new value</th></tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>
                                    <lt-highlighter contenteditable="false" style="display: none;" data-lt-linked="1"><lt-div spellcheck="false" class="lt-highlighter__wrapper" style="width: 268.938px !important; height: 24px !important; transform: none !important; transform-origin: 134.469px 12px !important; zoom: 1 !important; margin-top: 8px !important;"><lt-div class="lt-highlighter__scroll-element" style="top: 0px !important; left: 0px !important; width: 268.938px !important; height: 24px !important;"></lt-div></lt-div></lt-highlighter>
                                    <p class="d-grid" style="margin-top: 8px;margin-bottom: auto;">Overlap percentage (%)</p>
                                </td>
                                <td class="text-center">
                                    <lt-highlighter contenteditable="false" style="display: none;" data-lt-linked="1"><lt-div spellcheck="false" class="lt-highlighter__wrapper" style="width: 192.938px !important; height: 24px !important; transform: none !important; transform-origin: 96.4688px 12px !important; zoom: 1 !important; margin-top: 8px !important;"><lt-div class="lt-highlighter__scroll-element" style="top: 0px !important; left: 0px !important; width: 192.938px !important; height: 24px !important;"></lt-div></lt-div></lt-highlighter>
                                    <p class="d-grid" style="margin-top: 8px;margin-bottom: auto;">${image["overlap"]}</p>
                                </td>
                                <td class="text-end" style="max-width: 150px;">
                                    <div class="input-group">
                                        <input id="p-overlap-${image["date"]}-input" type="text" class="form-control">
                                        <button id="p-overlap-${image["date"]}-update-button" class="btn btn-primary" type="button">Update</button>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <lt-highlighter contenteditable="false" style="display: none;" data-lt-linked="1"><lt-div spellcheck="false" class="lt-highlighter__wrapper" style="width: 268.938px !important; height: 24px !important; transform: none !important; transform-origin: 134.469px 12px !important; zoom: 1 !important; margin-top: 8px !important;"><lt-div class="lt-highlighter__scroll-element" style="top: 0px !important; left: 0px !important; width: 268.938px !important; height: 24px !important;"></lt-div></lt-div></lt-highlighter>
                                    <p class="d-grid" style="margin-top: 8px;margin-bottom: auto;">Blending</p>
                                </td>
                                <td class="text-center"><lt-highlighter contenteditable="false" style="display: none;" data-lt-linked="1">
                                    <lt-div spellcheck="false" class="lt-highlighter__wrapper" style="width: 192.938px !important; height: 24px !important; transform: none !important; transform-origin: 96.4688px 12px !important; zoom: 1 !important; margin-top: 8px !important;">
                                    <lt-div class="lt-highlighter__scroll-element" style="top: 0px !important; left: 0px !important; width: 192.938px !important; height: 24px !important;"></lt-div>
                                    </lt-div>
                                    </lt-highlighter>

                                    <p class="d-grid" style="margin-top: 8px;margin-bottom: auto;">${image["blending"]}</p>
                                </td>
                                <td class="text-end" style="max-width: 150px;">
                                    <div class="input-group">
                                        <select id="blending-${image["date"]}-select" class="form-select">
                                            <option value="OVERLAY" selected="true">Overlay</option>
                                            <option value="LINEAR">Linear</option>
                                            <option value="AVERAGE">Average</option>
                                        </select>
                                        <button id="blending-${image["date"]}-update-button" class="btn btn-primary" type="button">Update</button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="modal-footer">
                <button id="restart-stacking-${image["date"]}-button" class="btn btn-light" type="button">Stacking <i class="inline-icon material-icons">&#xe5d5;</i></button>
                <button id="restart-correction-${image["date"]}-button" class="btn btn-light" type="button">Correction <i class="inline-icon material-icons">&#xe5d5;</i></button>
                <button id="restart-stitching-${image["date"]}-button" class="btn btn-light" type="button">Stitching <i class="inline-icon material-icons">&#xe5d5;</i></button>
                <button id="restart-all-${image["date"]}-button" class="btn btn-success" type="button">All tasks <i class="inline-icon material-icons">&#xe5d5;</i></button>
                <button id="delete-${image["date"]}-button" class="btn btn-danger" type="button" data-bs-dismiss="modal"><i class="inline-icon material-icons">&#xe872;</i></button>
            </div>
        </div>
    </div>
    `
};

const removeAllChildNodes = (parent) => {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}

const fetch_images = async () => {
    // images_list.innerHTML = "";
    removeAllChildNodes(images_list);

    const url = new URL(analyse_url.href + "images_meta")
    const images_meta = await execute_get_rest_call(url)

    for (let i=images_meta.length-1; i>=0; i--) {
        const image = images_meta[i];

        image_date = image["date"].replace(/_/g, '-')
        body.insertAdjacentHTML("beforeend", template_modal_settings(image));

        const entry = (
            `<li class="list-group-item">` +
                `<div class="row" id="${image["date"]}_${image["name"]}">` + 
                    `<div class="col-3 d-flex d-lg-flex flex-grow-1 justify-content-center align-items-center align-content-stretch align-self-stretch justify-content-lg-center justify-content-xxl-center align-items-xxl-center" style="border-right: 1.5px solid var(--bs-gray-300);border-left-style: none;"><img src="${analyse_url.href}images/heightmap.png?date=${image["date"]}" width="80px" /><span>${image["date"]}<br />${image["name"]? image["name"] : "Nameless"}</span></div>` +
                    `<div class="col-1 d-flex d-lg-flex flex-grow-1 justify-content-center align-items-center align-content-stretch align-self-stretch justify-content-lg-center justify-content-xxl-center align-items-xxl-center" style="border-right: 1.5px solid var(--bs-gray-300);border-left-style: none;"><span id="${image["date"]}_${image["name"]}_stacked" style="text-align: center;"><br />${image["focus_stacked"] ? success_str : pending_str}<br /><br /></span></div>` +
                    `<div class="col-1 d-flex d-lg-flex flex-grow-1 justify-content-center align-items-center align-content-stretch align-self-stretch justify-content-lg-center justify-content-xxl-center align-items-xxl-center" style="border-right: 1.5px solid var(--bs-gray-300);border-left-style: none;"><span id="${image["date"]}_${image["name"]}_correction" style="text-align: center;border-right: 1.5px none var(--bs-gray-400);">${image["correction"] ? success_str : pending_str}<br /></span></div>` +
                    `<div class="col-1 d-flex d-lg-flex flex-grow-1 justify-content-center align-items-center align-content-stretch align-self-stretch justify-content-lg-center justify-content-xxl-center align-items-xxl-center" style="border-right: 1.5px solid var(--bs-gray-300);border-left-style: none;"><span id="${image["date"]}_${image["name"]}_stitched" style="text-align: center;">${image["stitched"] ? success_str : pending_str}<br /></span></div>` +
                    `<div class="col-1 d-flex d-lg-flex flex-grow-1 justify-content-center align-items-center align-content-stretch align-self-stretch justify-content-lg-center justify-content-xxl-center align-items-xxl-center"><span style="text-align: center;"><br /></span><button id="${image["date"]}-button" class="btn btn-primary" type="button" style="width: 50px;" data-bs-toggle="modal" data-bs-target="#modal-${image["date"]}"><i class="inline-icon material-icons">settings</i></button></div>` +
                `</div>` +
            `</li>`
        );
        images_list.insertAdjacentHTML("beforeend", entry);
    }

    // add event listener
    for (let i=images_meta.length-1; i>=0; i--) {
        const image = images_meta[i];
        
        document.getElementById(`delete-${image["date"]}-button`).addEventListener("click", async () => {
            delete_image_from_db(image["name"], image["date"]);
        });

        document.getElementById(`restart-stacking-${image["date"]}-button`).addEventListener("click", async () => {
            restart_task(image["date"], "stacking");
        });

        document.getElementById(`restart-correction-${image["date"]}-button`).addEventListener("click", async () => {
            restart_task(image["date"], "correction");
        });

        document.getElementById(`restart-stitching-${image["date"]}-button`).addEventListener("click", async () => {
            restart_task(image["date"], "stitching");
        });

        document.getElementById(`p-overlap-${image["date"]}-update-button`).addEventListener("click", () => {
            update_setting(image["date"], "overlap", document.getElementById(`p-overlap-${image["date"]}-input`).value);
            document.location.reload();
        });

        document.getElementById(`blending-${image["date"]}-update-button`).addEventListener("click", (e) => {
            const blending_select = document.getElementById(`blending-${image["date"]}-select`);
            update_setting(image["date"], "blending", blending_select.value);
        });
    }

}

(() => {
    fetch_images()
    setInterval(update_busy_tasks, 500);
    setTimeout(document.reload,60000);
})();