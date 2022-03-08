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

export default angular.module('tga', [])
    .run(['$templateCache', ($templateCache) => {
        // Add Crossref Transmitter Settings template
        $templateCache.put(
            'crossref_http_config.html',
            require('./views/crossref_http_config.html'),
        );
    }]);
