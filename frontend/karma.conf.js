// Karma configuration for the frontend unit tests.
// Run with:  npm test   (from the frontend folder)
module.exports = function (config) {
  config.set({
    frameworks: ['jasmine'],
    files: [
      'lib/angular.min.js',
      'lib/angular-mocks.min.js',
      'js/services.js',
      'tests/*.spec.js'
    ],
    browsers: ['ChromeHeadless'],
    singleRun: true,
    autoWatch: false
  });
};
