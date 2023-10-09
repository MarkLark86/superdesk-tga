from typing import List
from typing_extensions import TypedDict


def get_input_id_from_label(label: str) -> str:
    return "input_" + label.replace(" ", "_").lower()


def render_text_input(label: str, value: str):
    input_id = get_input_id_from_label(label)

    return f"""
<div class="form__item">
    <div class="sd-input sd-input--medium">
        <label class="sd-input__label" for="{input_id}">{label}</label>
        <div class="sd-input__input-container">
            <input id="{input_id}" type="text" class="sd-input__input" disabled value="{value}" />
        </div>
    </div>
</div>
"""


def render_content_text(label: str, value: str):
    input_id = get_input_id_from_label(label)

    return f"""
<div class="sd-input sd-input--x-large sd-input--boxed-style sd-input--boxed-label">
    <label class="sd-input__label sd-input__label--boxed" for="{input_id}">
        {label}
    </label>
    <div class="sd-input__input-container">
        <input id="{input_id}" class="sd-input__input" type="text" disabled value="{value}" />
    </div>
</div>
"""


def render_html_content(label: str, value: str):
    input_id = get_input_id_from_label(label)

    return f"""
<div class="sd-input sd-input--x-large sd-input--boxed-style sd-input--boxed-label">
    <label class="sd-input__label sd-input__label--boxed" for="{input_id}">
        {label}
    </label>
    <div class="sd-input__input-container">
        <div id="{input_id}" class="html-preview">
            {value}
        </div>
    </div>
</div>
"""


class CVItem(TypedDict):
    name: str


def render_tag_list(label: str, values: List[str]):
    input_id = get_input_id_from_label(label)
    value_list = "".join(
        [
            f"""<li class="p-chips-token p-highlight"><span class="p-chips-token-label">{value}</span></li>"""
            for value in values
        ]
    )
    chip_classes = "p-chips p-component p-inputwrapper tags-input--multi-select sd-input__input  p-inputwrapper-filled"

    return f"""
<div class="form__item">
    <div class="sd-input sd-input--medium">
        <label class="sd-input__label" for="{input_id}">{label}</label>
        <div class="sd-input__input-container">
            <div class="{chip_classes}" style="cursor: not-allowed !important;">
                <ul id="{input_id}" class="p-inputtext p-chips-multiple-container">
                    {value_list}
                </ul>
            </div>
        </div>
    </div>
</div>
"""


def render_featuremedia_image(item):
    featuremedia = item["associations"]["featuremedia"]
    image_url = featuremedia["renditions"]["viewImage"]["href"]
    alt_text = featuremedia["alt_text"]

    return f"""
<div class="sd-input sd-input--x-large sd-input--boxed-style sd-input--boxed-label">
    <label class="sd-input__label sd-input__label--boxed" for="input_featuremedia">
        Featuremedia
    </label>
    <div class="sd-input__input-container">
        <figure>
            <img id="input_featuremedia" src="{image_url}" alt="{alt_text}" />
            <figcaption>{alt_text}</figcaption>
        </figure>
    </div>
</div>
"""


def render_cv_items(label: str, values: List[CVItem]):
    return render_tag_list(label, [value["name"] for value in values])
