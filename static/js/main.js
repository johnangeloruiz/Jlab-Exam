// Main JavaScript for Survey Application

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000);
        }
    });

    // Form validation
    $('form').on('submit', function(e) {
        var form = this;
        if (form.checkValidity() === false) {
            e.preventDefault();
            e.stopPropagation();
        }
        $(form).addClass('was-validated');
    });

    // Auto-save functionality for forms
    $('input, textarea, select').on('change', function() {
        var form = $(this).closest('form');
        if (form.attr('id') === 'questionForm') {
            // Auto-save question form data
            saveFormData(form);
        }
    });

    // Load saved form data
    loadFormData();

    // Question type change handler for dynamic required attribute
    $('#questionType').on('change', function() {
        const type = $(this).val();
        const optionsSection = $('#optionsSection');
        const ratingSection = $('#ratingSection');
        const optionInputs = $('.option-input');

        // Hide all sections
        optionsSection.hide();
        ratingSection.hide();

        // Show relevant sections and set required attribute
        if (type === 'multiple_choice' || type === 'dropdown') {
            optionsSection.show();
            optionInputs.attr('required', 'required');
        } else {
            optionInputs.removeAttr('required');
            if (type === 'rating') {
                ratingSection.show();
            }
        }

        // If you have a preview function, call it here
        if (typeof updatePreview === 'function') {
            updatePreview();
        }
    });
});

// Utility Functions
function showAlert(message, type = 'info') {
    var alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    $('.container-fluid').first().prepend(alertHtml);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
}

function showLoading(element) {
    $(element).html('<i class="fas fa-spinner fa-spin"></i> Loading...');
}

function hideLoading(element, originalText) {
    $(element).html(originalText);
}

// AJAX Helper Functions
function makeRequest(url, method = 'GET', data = null) {
    return $.ajax({
        url: url,
        method: method,
        data: data,
        contentType: 'application/json',
        dataType: 'json'
    });
}

// Form Data Management
function saveFormData(form) {
    var formData = {};
    $(form).find('input, textarea, select').each(function() {
        if ($(this).attr('name')) {
            if ($(this).attr('type') === 'checkbox') {
                formData[$(this).attr('name')] = $(this).is(':checked');
            } else if ($(this).attr('type') === 'radio') {
                if ($(this).is(':checked')) {
                    formData[$(this).attr('name')] = $(this).val();
                }
            } else {
                formData[$(this).attr('name')] = $(this).val();
            }
        }
    });
    
    localStorage.setItem('form_' + form.attr('id'), JSON.stringify(formData));
}

function loadFormData() {
    $('form').each(function() {
        var form = $(this);
        var formId = form.attr('id');
        if (formId) {
            var savedData = localStorage.getItem('form_' + formId);
            if (savedData) {
                try {
                    var data = JSON.parse(savedData);
                    $.each(data, function(name, value) {
                        var element = form.find('[name="' + name + '"]');
                        if (element.length) {
                            if (element.attr('type') === 'checkbox') {
                                element.prop('checked', value);
                            } else if (element.attr('type') === 'radio') {
                                element.filter('[value="' + value + '"]').prop('checked', true);
                            } else {
                                element.val(value);
                            }
                        }
                    });
                } catch (e) {
                    console.error('Error loading form data:', e);
                }
            }
        }
    });
}

function clearFormData(formId) {
    localStorage.removeItem('form_' + formId);
}

// Question Management Functions
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showAlert('Copied to clipboard!', 'success');
    }, function(err) {
        console.error('Could not copy text: ', err);
        showAlert('Failed to copy to clipboard', 'danger');
    });
}

// Chart Helper Functions
function createChart(canvasId, data, type = 'bar') {
    var ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: type,
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: data.title || 'Chart'
                }
            },
            scales: type === 'bar' ? {
                y: {
                    beginAtZero: true
                }
            } : {}
        }
    });
}

// Survey Functions
function validateSurveyForm() {
    var isValid = true;
    var firstInvalidField = null;
    
    $('.question-card').each(function() {
        var questionCard = $(this);
        var requiredInputs = questionCard.find('[required]');
        
        requiredInputs.each(function() {
            var input = $(this);
            if (!input.val() || (input.attr('type') === 'radio' && !input.is(':checked'))) {
                isValid = false;
                if (!firstInvalidField) {
                    firstInvalidField = input;
                }
            }
        });
    });
    
    if (!isValid && firstInvalidField) {
        firstInvalidField.focus();
        showAlert('Please answer all required questions before submitting.', 'warning');
    }
    
    return isValid;
}

// Animation Functions
function animateCounter(element, start, end, duration = 2000) {
    var startTimestamp = null;
    var step = function(timestamp) {
        if (!startTimestamp) startTimestamp = timestamp;
        var progress = Math.min((timestamp - startTimestamp) / duration, 1);
        var current = Math.floor(progress * (end - start) + start);
        $(element).text(current);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Export Functions
function exportToCSV(data, filename = 'export.csv') {
    var csv = convertToCSV(data);
    var blob = new Blob([csv], { type: 'text/csv' });
    var url = window.URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    var headers = Object.keys(data[0]);
    var csv = headers.join(',') + '\n';
    
    data.forEach(function(row) {
        var values = headers.map(function(header) {
            var value = row[header];
            if (typeof value === 'string' && value.includes(',')) {
                value = '"' + value + '"';
            }
            return value;
        });
        csv += values.join(',') + '\n';
    });
    
    return csv;
}

// Error Handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    showAlert('An unexpected error occurred. Please refresh the page.', 'danger');
});

// Performance Monitoring
function measurePerformance(name, fn) {
    var start = performance.now();
    var result = fn();
    var end = performance.now();
    console.log(`${name} took ${end - start} milliseconds`);
    return result;
}

// Local Storage Helpers
function setLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.error('Error saving to localStorage:', e);
    }
}

function getLocalStorage(key, defaultValue = null) {
    try {
        var item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.error('Error reading from localStorage:', e);
        return defaultValue;
    }
}

// Theme Functions
function toggleTheme() {
    var currentTheme = getLocalStorage('theme', 'light');
    var newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setLocalStorage('theme', newTheme);
    applyTheme(newTheme);
}

function applyTheme(theme) {
    if (theme === 'dark') {
        $('body').addClass('dark-theme');
    } else {
        $('body').removeClass('dark-theme');
    }
}

// Initialize theme on page load
$(document).ready(function() {
    var savedTheme = getLocalStorage('theme', 'light');
    applyTheme(savedTheme);
});

function addOption(questionId) {
    var questionOptionsContainer = $(`#questionOptions_${questionId}`);
    var optionCount = questionOptionsContainer.children('.input-group').length + 1;
    
    var newOption = $(`
        <div class="input-group mb-2">
            <input type="text" class="form-control option-input" name="option[]" placeholder="Option ${optionCount}" required>
            <button type="button" class="btn btn-outline-danger" onclick="removeOption(this)">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `);
    
    questionOptionsContainer.append(newOption);
}

function removeOption(button) {
    $(button).closest('.input-group').remove();
}
