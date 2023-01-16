import {IEditorComponentProps} from 'superdesk-api';

export interface IProfileTextFieldConfig {
    use_editor_3: boolean;
    exclude_from_content_api: boolean;
}

export type IProfileTextFieldProps = IEditorComponentProps<string | undefined, IProfileTextFieldConfig>;
