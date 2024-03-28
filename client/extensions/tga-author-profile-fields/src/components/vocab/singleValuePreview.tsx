import * as React from 'react';

import {IPreviewComponentProps} from 'superdesk-api';
import {IVocabularyFieldValue, IVocabularyFieldConfig} from './interfaces';

type IProps = IPreviewComponentProps<IVocabularyFieldValue, IVocabularyFieldConfig>;

export class SingleVocabularyPreview extends React.PureComponent<IProps> {
    render() {
        return this.props.value == null || this.props.value.length === 0 ? null : (
            <div className="form__row form__row--small-padding">
                <p className="sd-text__normal">
                    {this.props.value.name}
                </p>
            </div>
        );
    }
}
