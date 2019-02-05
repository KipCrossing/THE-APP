import Vue from "vue";

import Vuex from 'vuex'
Vue.use(Vuex)

import VueRouter from "vue-router";
Vue.use(VueRouter);

import * as VApp from 'vuetify/es5/components/VApp'
import Vuetify from 'vuetify/es5/components/Vuetify'
import VIcon from 'vuetify/es5/components/VIcon'
import * as VMenu from 'vuetify/es5/components/VMenu'
import VBtn from 'vuetify/es5/components/VBtn'
import VCard from 'vuetify/es5/components/VCard'
import VDatePicker from 'vuetify/es5/components/VDatePicker'
import * as VForm from 'vuetify/es5/components/VForm'
import VProgressCircular from 'vuetify/es5/components/VProgressCircular'
import VSubheader from 'vuetify/es5/components/VSubheader'
import * as VToolbar from 'vuetify/es5/components/VToolbar'
import VTooltip from 'vuetify/es5/components/VTooltip'
import VTextarea from 'vuetify/es5/components/VTextarea'
import VTextField from 'vuetify/es5/components/VTextField'
import VAutocomplete from 'vuetify/es5/components/VAutocomplete'
import VSelect from 'vuetify/es5/components/VSelect'
import VSwitch from 'vuetify/es5/components/VSwitch'
import VBottomNav from 'vuetify/es5/components/VBottomNav'
import * as VList from 'vuetify/es5/components/VList'
import * as VNavigationDrawer from 'vuetify/es5/components/VNavigationDrawer'
import VFooter from 'vuetify/es5/components/VFooter'
import VDivider from 'vuetify/es5/components/VDivider'
import VAlert from 'vuetify/es5/components/VAlert'
import * as VGrid from 'vuetify/es5/components/VGrid'
import transitions from 'vuetify/es5/components/transitions'
import directives from 'vuetify/es5/directives'

import VuetifyAll from 'vuetify'
import 'vuetify/dist/vuetify.min.css'
import colors from 'vuetify/es5/util/colors'

import linkify from 'vue-linkify'
Vue.directive('linkified', linkify)

// @ts-ignore
Vue.use(Vuetify, {
    components: {
        ...VApp,
        ...VList,
        ...VToolbar,
        ...VForm,
        ...VMenu,
        ...VNavigationDrawer,
        ...VGrid,
        VBottomNav,
        VAlert,
        VFooter,
        transitions,
        VIcon,
        VTextarea,
        VTextField,
        VAutocomplete,
        VSelect,
        VSwitch,
        VBtn,
        VDatePicker,
        VProgressCircular,
        VSubheader,
        VTooltip,
        VDivider,
        VCard,
    },
    directives,
    iconfont: 'mdi',
    // https://vuetifyjs.com/en/theme-generator
    theme: {
        primary: colors.blue.darken1,
        secondary: colors.blue.lighten3,
        accent: colors.amber.darken4,
        error: colors.red.base,
        warning: colors.yellow.darken3,
        info: colors.blue.base,
        success: colors.green.base
    }
})

import VueResource from "vue-resource";
Vue.use(VueResource);

import Notifications from "vue-notification";
Vue.use(Notifications);

import FluxApi from "./lib/api";
Vue.use(FluxApi);

import ErrHandlers from "./lib/errors";
Vue.use(ErrHandlers);

import { FluxUtils } from "./lib/fluxUtils";
Vue.use(FluxUtils);

import ToggleButton from 'vue-js-toggle-button'
Vue.use(ToggleButton)

import vueSignature from "vue-signature"
Vue.use(vueSignature)


import App from "./App.vue";


import Dashboard from "@c/Dashboard.vue";
import UserValidation from "@c/UserValidation.vue";
import UserDetailsMain from "@c/UserDetails";
import UserRevocation from "@c/UserRevocation.vue";
import * as QAndA from "@c/QAndA";
import * as Finance from "@c/Finance";
import * as Volunteers from "@c/Volunteers"
import * as Candidates from "@c/Candidates"
import AuditRoles from "@c/Admin/AuditRoles.vue";
import FinanceEnterDonation from "@c/Finance/FinanceEnterDonation.vue";

import R from "./routes";

import {UiSection, Loading, Error, Warning, FluxInput, TransitionExpand, TransitionSlide, CollapsibleSection} from "@c/common";
import NavDrawer from '@c/NavDrawer.vue';
Vue.component('ui-section', UiSection);
Vue.component('ui-collapsible', CollapsibleSection);
Vue.component('loading', Loading);
Vue.component('error', Error);
Vue.component('warning', Warning);
Vue.component('flux-input', FluxInput);
Vue.component('transition-slide', TransitionSlide);
Vue.component('transition-expand', TransitionExpand);
Vue.component('nav-drawer', NavDrawer);

const routes = [
    { path: R.Dashboard, component: Dashboard },
    { path: R.ValidateSelf, component: UserValidation },
    { path: R.EditUserDetails, component: UserDetailsMain },
    { path: R.MembershipRevocation, component: UserRevocation },

    { path: R.QAndA, component: QAndA.QAndA },
    { path: R.QandaAskQuestion, component: QAndA.AskQuestion },
    { path: R.QandaReply, component: QAndA.QAndAReply },
    { path: R.QandaThread, component: QAndA.Thread },
 
    { path: R.AdminAuditRoles, component: AuditRoles },
    { path: R.FinanceMenu, component: Finance.Menu },
    { path: R.FinanceDonationEntry, component: Finance.EnterDonation },
    { path: R.FinanceDonationLog, component: Finance.DonationLog },
    { path: R.VolunteerNdaStatusAndSign, component: Volunteers.NdaStatusAndSign },
    // { path: R.VolunteerSignNDA, component: Volunteers.SignNDA },
    { path: R.CandidateDashboard, component: Candidates.Dashboard },
    { path: "*", redirect: "/" }
];

const router = new VueRouter({ routes });


import { store } from './store'
import 'roboto-fontface/css/roboto/roboto-fontface.css'
import '@mdi/font/css/materialdesignicons.css'


import VueGoodTablePlugin from 'vue-good-table'
import './css/vendor/vue-good-table.min.css'
Vue.use(VueGoodTablePlugin)
import { VueGoodTable } from 'vue-good-table'
Vue.component('good-table', VueGoodTable)


new Vue({
    router,
    store,
    render: h => h(App)
}).$mount("#app");
