import {IExtension, IExtensionActivationResult, ICustomFieldType, ICommonFieldConfig} from 'superdesk-api';
import {superdesk} from './superdesk';
import {IPublishSignOffValue} from './interfaces';

import {UserSignOffField} from './components/fields/editor';
import {UserSignOffPreview} from './components/fields/preview';
import {UserSignOffTemplate} from './components/fields/template';

const extension: IExtension = {
    activate: () => {
        const {gettext} = superdesk.localization;
        const signOffField: ICustomFieldType<IPublishSignOffValue, IPublishSignOffValue, ICommonFieldConfig, never> = {
            id: 'tga-sign-off',
            label: gettext('User Sign Off'),
            editorComponent: UserSignOffField,
            previewComponent: UserSignOffPreview,
            templateEditorComponent: UserSignOffTemplate,

            hasValue: (value) => value != null,
            getEmptyValue: () => null,
        };

        const result: IExtensionActivationResult = {
            contributions: {
                customFieldTypes: [signOffField],
            },
        };

        return Promise.resolve(result);
    }
}

export default extension;
