let course_select = document.getElementById('course_select');
let section_select = document.getElementById('section_select');

function update_sections()
{
    let course_id = course_select.value;
    for (section of section_select.options)
        section.hidden = section.id !== course_id;
}

update_sections();

course_select.addEventListener('change', () =>
{
    section_select.selectedIndex = 0;
    section_select.hidden = false;
    update_sections();
});
