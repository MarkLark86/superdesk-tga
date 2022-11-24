import * as React from 'react';

import {IConfigComponentProps, IVocabulary} from 'superdesk-api';
import {superdesk} from '../../superdesk';
import {Select, Option, Switch} from 'superdesk-ui-framework/react';
import {IVocabularyFieldConfig} from './interfaces';

function getVocabularies(): Promise<Array<IVocabulary>> {
    const {dataApi} = superdesk;

    return dataApi.query<IVocabulary>(
        'vocabularies',
        1,
        {field: 'display_name', direction: 'ascending'},
        {
            $and: [
                {field_type: {$exists: false, $eq: null}},
                {custom_field_type: {$exists: false, $eq: null}},
            ],
        }
    ).then((vocabularies) => {
        return vocabularies._items;
    })
}

type IProps = IConfigComponentProps<IVocabularyFieldConfig>;
interface IState {
    cvs: Array<IVocabulary>
}


export class VocabularyFieldConfig extends React.Component<IProps, IState> {
    constructor(props: IProps) {
        super(props);

        this.state = {cvs: []};
    }

    componentDidMount() {
        getVocabularies().then((cvs) => {
            this.setState({cvs: cvs});
            if (!this.props.config?.vocabulary_name) {
                this.props.onChange({
                    vocabulary_name: cvs[0]._id,
                    allow_freetext: this.props.config?.allow_freetext ?? false,
                });
            }
        });
    }

    render() {
        const config = this.props.config ?? {
            vocabulary_name: '',
            allow_freetext: false,
        };
        const {Spacer} = superdesk.components;
        const {gettext} = superdesk.localization;

        return (
            <Spacer type="vertical" spacing="medium">
                <Select
                    value={config?.vocabulary_name}
                    label={gettext('Vocabulary')}
                    onChange={(cv_id) => {
                        this.props.onChange({
                            ...config,
                            vocabulary_name: cv_id,
                        });
                    }}
                >
                    {this.state.cvs.map((cv) => (
                        <Option key={cv._id} value={cv._id}>{cv.display_name}</Option>
                    ))}
                </Select>
                <Switch
                    label={{text: gettext('Allow Freetext')}}
                    value={config?.allow_freetext == true}
                    onChange={(allow_freetext) => {
                        this.props.onChange({
                            ...config,
                            allow_freetext: allow_freetext,
                        });
                    }}
                />
            </Spacer>
        );
    }
}
