let course_select = document.getElementById('course_select');
let section_select = document.getElementById('section_select');

function update_sections(e)
{
    let course_id = e.target.value;
    section_select.hidden = false;
    section_select.selectedIndex = 0;

    for (section of section_select.options)
        section.hidden = section.id !== course_id;
}

course_select.addEventListener('change', update_sections);
