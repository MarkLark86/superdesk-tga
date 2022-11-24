import * as React from 'react';

import {IPreviewComponentProps, IVocabularyItem,} from 'superdesk-api';
import {FormLabel} from 'superdesk-ui-framework/react';

export class VocabularyPreview extends React.PureComponent<IPreviewComponentProps> {
    render() {
        const item: IVocabularyItem = this.props.value;

        return (
            <div className="form__row form__row--small-padding">
                <FormLabel
                    text={this.props.field.display_name}
                    style="light"
                />
                <p className="sd-text__normal">
                    {item.name}
                </p>
            </div>
        );
    }
}
