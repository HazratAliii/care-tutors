angular.module('libraryApp', ['ngRoute', 'library.services'])

.config(['$locationProvider', '$routeProvider', function ($locationProvider, $routeProvider) {
  $locationProvider.hashPrefix('');

  $routeProvider
    .when('/books', {
      templateUrl: 'views/book-list.html',
      controller: 'BooksCtrl',
      controllerAs: 'vm'
    })
    .when('/books/new', {
      templateUrl: 'views/book-form.html',
      controller: 'BookFormCtrl',
      controllerAs: 'vm'
    })
    .when('/books/:id/edit', {
      templateUrl: 'views/book-form.html',
      controller: 'BookFormCtrl',
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
}])

.controller('BookFormCtrl', ['BookService', '$routeParams', '$location',
    function (BookService, $routeParams, $location) {
  var vm = this;

  vm.isEdit = !!$routeParams.id;
  vm.currentYear = new Date().getFullYear();
  vm.book = { title: '', author: '', category: '', published_year: null };
  vm.loading = vm.isEdit;
  vm.pageError = '';
  vm.serverError = '';
  vm.saving = false;

  if (vm.isEdit) {
    BookService.get($routeParams.id).then(function (response) {
      var book = response.data;
      vm.book = {
        title: book.title,
        author: book.author,
        category: book.category,
        published_year: book.published_year
      };
    }, function (response) {
      vm.pageError = (response.data && response.data.error) || 'Could not load the book.';
    }).finally(function () {
      vm.loading = false;
    });
  }

  vm.save = function () {
    vm.serverError = '';
    if (vm.form.$invalid) { return; }

    vm.saving = true;
    var promise = vm.isEdit
      ? BookService.update($routeParams.id, vm.book)
      : BookService.create(vm.book);

    promise.then(function () {
      $location.path('/books');
    }, function (response) {
      vm.serverError = (response.data && response.data.error) || 'Could not save the book.';
      vm.saving = false;
    });
  };

  vm.cancel = function () {
    $location.path('/books');
  };
}]);
