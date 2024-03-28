import {IExtension, IExtensionActivationResult, ICustomFieldType, ICommonFieldConfig} from 'superdesk-api';
import {superdesk} from './superdesk';

import {ProfileIDField, IProfileIdValue} from './components/profileId/editor';
import {ProfileIdPreview} from './components/profileId/preview';

import {IProfileTextValue, IProfileTextFieldConfig} from './components/profileText/interfaces';
import {ProfileTextField} from './components/profileText/editor';
import {ProfileTextPreview} from './components/profileText/preview';
import {ProfileTextFieldConfig} from './components/profileText/config';


import {IVocabularyFieldArrayValue, IVocabularyFieldConfig, IVocabularyFieldValue} from './components/vocab/interfaces';
import {VocabularyField} from './components/vocab/editor';
import {VocabularyFieldConfig} from './components/vocab/config';
import {VocabularyTypeaheadField} from './components/vocab/typeaheadEditor';
import {VocabularyPreview} from './components/vocab/preview';
import {SingleVocabularyPreview} from './components/vocab/singleValuePreview';

const extension: IExtension = {
    activate: () => {
        const {gettext} = superdesk.localization;

        const profileIdField: ICustomFieldType<IProfileIdValue, IProfileIdValue, ICommonFieldConfig, never> = {
            id: 'profile-id',
            label: gettext('Profile ID'),
            editorComponent: ProfileIDField,
            previewComponent: ProfileIdPreview,
            hasValue: (value) => value != null,
            getEmptyValue: () => undefined,
        };

        const profileTextField: ICustomFieldType<
            IProfileTextValue,
            IProfileTextValue,
            IProfileTextFieldConfig,
            never
        > = {
            id: 'profile-text',
            label: gettext('Profile Text'),
            editorComponent: ProfileTextField,
            previewComponent: ProfileTextPreview,
            configComponent: ProfileTextFieldConfig,
            hasValue: (value) => value != null,
            getEmptyValue: () => undefined,
        };

        const vocabularyField: ICustomFieldType<
            IVocabularyFieldArrayValue,
            IVocabularyFieldArrayValue,
            IVocabularyFieldConfig,
            never
        > = {
            id: 'vocabulary-field',
            label: gettext('Vocabulary Field'),
            editorComponent: VocabularyField,
            previewComponent: VocabularyPreview,
            configComponent: VocabularyFieldConfig,
            hasValue: (value) => value != null,
            getEmptyValue: () => undefined,
        };
        const vocabularyTypeaheadField: ICustomFieldType<
            IVocabularyFieldValue,
            IVocabularyFieldValue,
            IVocabularyFieldConfig,
            never
        > = {
            id: 'vocabulary-typeahead-field',
            label: gettext('Vocabulary Typeahead Field'),
            editorComponent: VocabularyTypeaheadField,
            previewComponent: SingleVocabularyPreview,
            configComponent: VocabularyFieldConfig,
            hasValue: (value) => value != null,
            getEmptyValue: () => undefined,
        };

        const result: IExtensionActivationResult = {
            contributions: {
                customFieldTypes: [
                    profileIdField,
                    profileTextField,
                    vocabularyField,
                    vocabularyTypeaheadField,
                ],
            },
        };

        return Promise.resolve(result);
    }
}

export default extension;
