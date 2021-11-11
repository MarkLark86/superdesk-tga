import {IExtension, IExtensionActivationResult} from 'superdesk-api';
import {superdesk} from './superdesk';

import {UserSignOffField} from './components/fields/editor';
import {UserSignOffPreview} from './components/fields/preview';
import {UserSignOffTemplate} from './components/fields/template';

const extension: IExtension = {
    activate: () => {
        const {gettext} = superdesk.localization;
        const result: IExtensionActivationResult = {
            contributions: {
                customFieldTypes: [
                    {
                        id: 'tga-sign-off',
                        label: gettext('User Sign Off'),
                        editorComponent: UserSignOffField,
                        previewComponent: UserSignOffPreview,
                        templateEditorComponent: UserSignOffTemplate,
                    }
                ],
            },
        };

        return Promise.resolve(result);
    }
}

export default extension;
