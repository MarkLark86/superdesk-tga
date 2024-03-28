import {ICommonFieldConfig} from 'superdesk-api';

export interface IProfileTextFieldConfig extends ICommonFieldConfig {
    use_editor_3: boolean;
    exclude_from_content_api: boolean;
}

export type IProfileTextValue = string | undefined;
