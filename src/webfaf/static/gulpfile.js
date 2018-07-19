var
  gulp = require('gulp'),
  del = require('del'),
  merge = require('merge-stream'),
  path = require('path'),
  concat = require('gulp-concat'),
  plumber = require('gulp-plumber'),
  rename = require('gulp-rename'),
  minifyCSS = require('gulp-clean-css'),
  minifyJS = require('gulp-uglify'),
  less = require('gulp-less'),
  npmfiles = require('gulp-npm-files'),

  filePath = {
    srcCSS: './src/css/*.css',
    srcJS: './src/js/*.js',
    srcLESS: './src/less/*.less',
    srcICONS: './src/icons/*.png',
    srcFONTS: './node_modules/patternfly/dist/fonts/*.{eot,otf,svg,ttf,woff,woff2}',

    dist: './dist',
    distCSS: './dist/css',
    distJS: './dist/js',
    distICONS: './dist/icons',
    distFONTS: './dist/fonts',

    node_modules: 'node_modules',
    flot: [
      './node_modules/flot/jquery.flot.js',
      './node_modules/flot/jquery.flot*.js',
      './node_modules/flot-axislabels/jquery.flot.axislabels.js'
    ],

    css_to_move: [
      './node_modules/bootstrap-multiselect/dist/css/bootstrap-multiselect.css',
      './node_modules/bootstrap-tagsinput/dist/bootstrap-tagsinput.css',
      './node_modules/daterangepicker/daterangepicker.css',
      './node_modules/typeahead.js-bootstrap-css/typeaheadjs.css'
    ],

    js_to_move: [
      './node_modules/bootstrap/dist/js/bootstrap.min.js',
      './node_modules/bootstrap-multiselect/dist/js/bootstrap-multiselect.js',
      './node_modules/bootstrap-tagsinput/dist/bootstrap-tagsinput.min.js',
      './node_modules/datatables/media/js/jquery.dataTables.min.js',
      './node_modules/daterangepicker/daterangepicker.js',
      './node_modules/jquery/dist/jquery.min.js',
      './node_modules/moment/min/moment.min.js',
      './node_modules/patternfly/dist/js/patternfly.min.js',
      './node_modules/typeahead.js/dist/typeahead.bundle.min.js'
    ],

    map_to_move: [
      './node_modules/bootstrap-tagsinput/dist/bootstrap-tagsinput.min.js.map',
      './node_modules/patternfly/node_modules/jquery/dist/jquery.min.map'
    ]
  };

/***  HELPER TASKS  ***/

/* Fonts */
gulp.task('build:fonts', function() {
  // move font files from patternfly to dist
  return gulp.src(filePath.srcFONTS)
    .pipe(gulp.dest(filePath.distFONTS));
});

/* Icons */
gulp.task('build:icons', function() {
  // move icons from src to dist
  return gulp.src(filePath.srcICONS)
    .pipe(gulp.dest(filePath.distICONS));
});

/* CSS */
gulp.task('build:css', ['copy:css', 'build:less'], function() {
  // move css files from source to dist
  return gulp.src(filePath.srcCSS)
    .pipe(plumber())
    .pipe(concat('style.min.css'))
    .pipe(minifyCSS())
    .pipe(plumber.stop())
    .pipe(gulp.dest(filePath.distCSS));
});

gulp.task('copy:css', function(){
  // move css files from node_modules to dist
  return gulp.src(filePath.css_to_move, { base: './' })
    .pipe(rename({ dirname: '' }))
    .pipe(gulp.dest(filePath.distCSS));
});

/* LESS */
gulp.task('build:less', function() {
  // compile less from source to css
  return gulp.src(filePath.srcLESS)
    .pipe(plumber())
    .pipe(less({
      paths: [ path.join(__dirname, filePath.node_modules),
               path.join(__dirname, filePath.node_modules + '/patternfly/node_modules') ]
    }))
    .pipe(minifyCSS())
    .pipe(rename({suffix: '.min'}))
    .pipe(plumber.stop())
    .pipe(gulp.dest(filePath.distCSS));
});

/* Javascript */
gulp.task('build:js', ['copy:js', 'js:flot'], function() {
  // move js files from source to dist
  return gulp.src(filePath.srcJS)
    .pipe(plumber())
    .pipe(minifyJS())
    .pipe(rename({
      dirname: '',
      suffix: '.min'
    }))
    .pipe(plumber.stop())
    .pipe(gulp.dest(filePath.distJS));
});

gulp.task('copy:js', ['copy:map'], function(){
  // move js files from node_modules to dist
  return gulp.src(filePath.js_to_move, { base: './' })
    .pipe(rename({ dirname: '' }))
    .pipe(gulp.dest(filePath.distJS))
});

gulp.task('js:flot', function(){
  // move and minify js files from node_modules/flot* to dist
  return gulp.src(filePath.flot, { base: './' })
    .pipe(plumber())
    .pipe(concat('jquery.flot.min.js'))
    .pipe(minifyJS())
    .pipe(plumber.stop())
    .pipe(gulp.dest(filePath.distJS));
});

/* JS Map Files */
gulp.task('copy:map', function(){
  // move js files from node_modules to dist
  return gulp.src(filePath.map_to_move, { base: './' })
    .pipe(rename({ dirname: '' }))
    .pipe(gulp.dest(filePath.distJS))
});

/* NPM Files  */
gulp.task('npm:dist', function() {
  return gulp.src(npmfiles(), { base: './' })
    .pipe(gulp.dest(filePath.dist));
});


/***  CLEANING TASKS  ***/
gulp.task('clean:dist', function() {
  return del.sync(filePath.dist);
});

gulp.task('clean:modules', function() {
  return del.sync(filePath.node_modules);
});

gulp.task('clean:all', ['clean:dist', 'clean:modules']);

/***  BUILDING TASKS  ***/
gulp.task('build:dist', ['build:css', 'build:js', 'build:fonts', 'build:icons']);
