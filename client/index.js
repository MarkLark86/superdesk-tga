import {startApp} from 'superdesk-core/scripts/index';

setTimeout(() => {
    startApp(
        [
            {
                id: 'planning-extension',
                load: () => import('superdesk-planning/client/planning-extension'),
            },
            {
                id: 'tga-sign-off',
                load: () => import('./extensions/tga-sign-off'),
            }
        ],
        {},
    );
});

export default angular.module('main.superdesk', []);
