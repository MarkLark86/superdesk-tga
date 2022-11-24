import {IEditorComponentProps, IVocabularyItem} from 'superdesk-api';

export interface IVocabularyFieldConfig {
    vocabulary_name: string;
    allow_freetext: boolean;
}

export type IVocabularyFieldProps = IEditorComponentProps<IVocabularyItem | null | undefined, IVocabularyFieldConfig>;
