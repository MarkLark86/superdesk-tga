import {IVocabularyItem, ICommonFieldConfig} from 'superdesk-api';

export interface IVocabularyFieldConfig extends ICommonFieldConfig {
    vocabulary_name: string;
    allow_freetext: boolean;
    exclude_from_content_api: boolean;
}

export type IVocabularyFieldValue = IVocabularyItem | null | undefined;
export type IVocabularyFieldArrayValue = Array<IVocabularyItem> | IVocabularyFieldValue;
