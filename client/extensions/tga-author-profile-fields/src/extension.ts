import {IExtension, IExtensionActivationResult} from 'superdesk-api';
import {superdesk} from './superdesk';

import {ProfileIDField} from './components/profileId/editor';

import {ProfileTextField} from './components/profileText/editor';
import {ProfileTextPreview} from './components/profileText/preview';
import {ProfileTextFieldConfig} from './components/profileText/config';

import {VocabularyField} from './components/vocab/editor';
import {VocabularyFieldConfig} from './components/vocab/config';
import {VocabularyTypeaheadField} from './components/vocab/typeaheadEditor';
import {VocabularyPreview} from './components/vocab/preview';

const extension: IExtension = {
    activate: () => {
        const {gettext} = superdesk.localization;
        const result: IExtensionActivationResult = {
            contributions: {
                customFieldTypes: [
                    {
                        id: 'profile-id',
                        label: gettext('Profile ID'),
                        editorComponent: ProfileIDField,
                    },
                    {
                        id: 'profile-text',
                        label: gettext('Profile Text'),
                        editorComponent: ProfileTextField,
                        previewComponent: ProfileTextPreview,
                        configComponent: ProfileTextFieldConfig,
                    },
                    {
                        id: 'vocabulary-field',
                        label: gettext('Vocabulary Field'),
                        editorComponent: VocabularyField,
                        previewComponent: VocabularyPreview,
                        configComponent: VocabularyFieldConfig,
                    },
                    {
                        id: 'vocabulary-typeahead-field',
                        label: gettext('Vocabulary Typeahead Field'),
                        editorComponent: VocabularyTypeaheadField,
                        previewComponent: VocabularyPreview,
                        configComponent: VocabularyFieldConfig,
                    },
                ],
            },
        };

        return Promise.resolve(result);
    }
}

export default extension;
