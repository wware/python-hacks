const pythonVariableName = /[a-zA-Z][a-zA-Z0-9]*/g;
let steps = [];
let which_step = 0;
let my_tables = {};
let most_recent_url = "";
let num_steps_to_process = 0;
let prefix = null;
let files = [];

function prepare_file(url) {
    if (my_tables[url]) {
        return;
    }
    if (prefix === null) {
        let before = "";
        let after = window.location.href;
        for (let i = 0; i < 3; i++) {
            let n = after.indexOf("/");
            before += after.substr(0, n + 1);
            after = after.substr(n + 1);
        }
        //prefix = before.substr(0, before.length - 1);
        prefix = before;
    }
    files.push(url);
    $.get(prefix + url).done(function(data) {
        let table = $('<table>');
        let linenum = 1;
        $.map(data.split("\n"), function (line) {
            let row = $('<tr id="L' + linenum + '">');
            let num = "" + linenum;
            while (num.length < 6) {
                num = " " + num;
            }
            line = num + "  " + line;
            let td = $('<td><code style="white-space: pre">'
                + line
                + '</code></td>');
            row.append(td);
            table.append(row);
            linenum += 1;
        });
        my_tables[url] = table;
	display_step();
    });
}

function display_file(url, vars, event, arg) {
    vars = JSON.parse(vars);
    if (url != most_recent_url) {
        most_recent_url = url;
        $('#filename').html('<h3>' + url + '</h3>');
        const target = $('div#target');
        target.empty();
        target.append(my_tables[url]);
    }
    let table = $('<table>')
        .attr('border', '1px solid black')
        .attr('border-collapse', 'collapse');
    for (key in vars) {
        const value = vars[key];
        table.append($(
            '<tr><td>' + key + '</td><td>'
            + value + '</td></tr>'));
    }
    $("#vars").empty();
    $("#vars").append(table);
    $("#returnvalue").empty();
    if (event == 'return') {
        let x = 'Return <tt>' + arg + '</tt>';
        $("#returnvalue").html(x);
    }
}
function unmark_line(selector) {
    $(selector).css("background-color", "");
}
function mark_line(selector) {
    const x = $(selector)[0];
    if (x != undefined) {
        x.scrollIntoView({block: "center"});
    }
    $(selector).css("background-color", "FF0");
}

function display_step() {
    let step = steps[which_step];
    display_file(files[parseInt(step.F)], step.V, step.E, step.A);
    mark_line("#L" + step.L);
}
function far_left_click() {
    left_click_inner(100);
}
function left_click() {
    left_click_inner(1);
}
function left_click_inner(n) {
    if (n === undefined)
        n = 1;
    let step1 = steps[which_step];
    unmark_line("#L" + step1.L);
    while (n > 0) {
        which_step--;
        if (which_step < 0) {
            which_step = 0;
            break;
        }
        n--;
    }
    display_step();
}
function right_click_inner(n) {
    let step1 = steps[which_step];
    while (n > 0) {
        which_step++;
        if (which_step > steps.length - 1) {
            which_step = steps.length - 1;
            break;
        }
        n--;
    }
    unmark_line("#L" + step1.L);
    display_step();
}
function right_click() {
    right_click_inner(1);
}
function far_right_click() {
    right_click_inner(100);
}
