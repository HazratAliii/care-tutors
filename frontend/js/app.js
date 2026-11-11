angular.module('libraryApp', ['ngRoute', 'library.services'])

.config(['$locationProvider', '$routeProvider', function ($locationProvider, $routeProvider) {
  $locationProvider.hashPrefix('');

  $routeProvider
    .when('/books', {
      templateUrl: 'views/book-list.html',
      controller: 'BooksCtrl',
      controllerAs: 'vm'
    })
    .otherwise({ redirectTo: '/books' });
}])

.controller('BooksCtrl', ['BookService', '$scope', '$window', function (BookService, $scope, $window) {
  var vm = this;

  vm.books = [];
  vm.categories = [];
  vm.search = '';
  vm.category = '';
  vm.loading = true;
  vm.error = '';

  function errorMessage(response) {
    return (response.data && response.data.error) ||
      'Could not reach the library API. Is the backend running?';
  }

  function refreshCategories() {
    // Only an unfiltered list contains every category, so the options are
    // rebuilt whenever the list is loaded without search or category set.
    var seen = {};
    vm.categories = [];
    vm.books.forEach(function (book) {
      if (book.category && !seen[book.category]) {
        seen[book.category] = true;
        vm.categories.push(book.category);
      }
    });
    vm.categories.sort();
  }

  function load() {
    vm.loading = true;
    vm.error = '';

    var params = {};
    if (vm.search) { params.search = vm.search; }
    if (vm.category) { params.category = vm.category; }

    BookService.list(params).then(function (response) {
      vm.books = response.data;
      if (!vm.search && !vm.category) {
        refreshCategories();
      }
    }, function (response) {
      vm.error = errorMessage(response);
    }).finally(function () {
      vm.loading = false;
    });
  }

  vm.borrow = function (book) {
    var name = $window.prompt('Who is borrowing "' + book.title + '"?');
    if (name === null) { return; }
    name = (name || '').trim();
    if (!name) {
      $window.alert('Borrower name is required.');
      return;
    }
    BookService.borrow(book.id, name).then(load, function (response) {
      $window.alert(errorMessage(response));
    });
  };

  vm.return = function (book) {
    BookService.returnBook(book.id).then(load, function (response) {
      $window.alert(errorMessage(response));
    });
  };

  vm.remove = function (book) {
    if (!$window.confirm('Delete "' + book.title + '"?')) { return; }
    BookService.remove(book.id).then(load, function (response) {
      $window.alert(errorMessage(response));
    });
  };

  $scope.$watchGroup(['vm.search', 'vm.category'], load);
  load();
}]);
