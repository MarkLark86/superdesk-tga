import {IEditorComponentProps} from 'superdesk-api';

export interface IProfileTextFieldConfig {
    use_editor_3: boolean;
}

export type IProfileTextFieldProps = IEditorComponentProps<string | undefined, IProfileTextFieldConfig>;
