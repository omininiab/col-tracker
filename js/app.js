const METRIC_CONFIG = {
    gasoline: {
        title: 'Gasoline (¢/L)',
        unit: '¢/L',
        description: 'Monthly average retail price for regular unleaded gasoline at self-service stations in Ottawa-Gatineau (StatCan Table 18-10-0001-01).',
        axisFormatter: (val) => val + '¢',
        tooltipFormatter: (val) => val + ' ¢/L'
    },
    milk: {
        title: 'Milk ($/4L)',
        unit: '$/4L',
        description: 'Canadian national monthly average retail price for a 4-litre container of milk, based on grocery transaction data (StatCan Table 18-10-0245-01).',
        axisFormatter: (val) => '$' + val,
        tooltipFormatter: (val) => '$' + val + ' / 4L'
    },
    bread_per_kg: {
        title: 'Bread ($/kg)',
        unit: '$/kg',
        description: 'Normalized retail price per kilogram of white bread, converted from standard 675g loaf scanner data across Canada (StatCan Table 18-10-0245-01).',
        axisFormatter: (val) => '$' + val,
        tooltipFormatter: (val) => '$' + val + ' / kg'
    },
    rent_index: {
        title: 'Rent (Index)',
        unit: 'Index',
        description: 'Consumer Price Index (CPI) measuring monthly price changes in rental accommodation across Canada (StatCan Table 18-10-0004-01).',
        axisFormatter: (val) => val,
        tooltipFormatter: (val) => val + ' (Index)'
    },
    owned_accommodation_index: {
        title: 'Home Ownership (Index)',
        unit: 'Index',
        description: 'Consumer Price Index (CPI) tracking owned accommodation costs including mortgage interest, replacement cost, and property taxes (StatCan Table 18-10-0004-01).',
        axisFormatter: (val) => val,
        tooltipFormatter: (val) => val + ' (Index)'
    },
    average_hourly_wage: {
        title: 'Average Wage ($/hr)',
        unit: '$/hr',
        description: 'Canada-wide average hourly wage rate across all industries and employees (Labour Force Survey, StatCan Table 14-10-0063-01).',
        axisFormatter: (val) => '$' + val,
        tooltipFormatter: (val) => '$' + val + ' / hr'
    },
    median_hourly_wage: {
        title: 'Median Wage ($/hr)',
        unit: '$/hr',
        description: 'Canada-wide median hourly wage rate across all industries and employees (Labour Force Survey, StatCan Table 14-10-0063-01).',
        axisFormatter: (val) => '$' + val,
        tooltipFormatter: (val) => '$' + val + ' / hr'
    },
    prime_rate: {
        title: 'Prime Rate (%)',
        unit: '%',
        description: 'Canadian chartered bank prime business lending rate, the benchmark interest rate for variable loans and lines of credit (Bank of Canada Valet API).',
        axisFormatter: (val) => val + '%',
        tooltipFormatter: (val) => val + '%'
    },
    electricity_index: {
        title: 'Electricity (Index)',
        unit: 'Index',
        description: 'Consumer Price Index (CPI) measuring relative price movements for household electricity across Canada (StatCan Table 18-10-0004-01).',
        axisFormatter: (val) => val,
        tooltipFormatter: (val) => val + ' (Index)'
    },
    clothing_index: {
        title: 'Clothing (Index)',
        unit: 'Index',
        description: 'Consumer Price Index (CPI) measuring relative price movements for clothing and footwear products across Canada (StatCan Table 18-10-0004-01).',
        axisFormatter: (val) => val,
        tooltipFormatter: (val) => val + ' (Index)'
    }
};

function formatTitle(key) {
    return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

// ==========================================
// Theme Management (Light / Dark Mode)
// ==========================================
function getStoredTheme() {
    try {
        const saved = localStorage.getItem('theme');
        return saved === 'light' || saved === 'dark' ? saved : null;
    } catch (error) {
        console.warn('Unable to read the saved theme preference:', error);
        return null;
    }
}

const prefersDarkTheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)');
let storedTheme = getStoredTheme();
let currentTheme = storedTheme || (prefersDarkTheme && prefersDarkTheme.matches ? 'dark' : 'light');
document.documentElement.setAttribute('data-theme', currentTheme);

function updateToggleUI(theme) {
    const toggleBtn = document.getElementById('theme-toggle');
    if (!toggleBtn) return;
    const icon = toggleBtn.querySelector('.theme-icon');
    const text = toggleBtn.querySelector('.theme-text');
    if (theme === 'dark') {
        icon.textContent = '☀';
        text.textContent = '';
        toggleBtn.setAttribute('aria-label', 'Switch to light mode');
        toggleBtn.setAttribute('aria-pressed', 'true');
    } else {
        icon.textContent = '☽';
        text.textContent = '';
        toggleBtn.setAttribute('aria-label', 'Switch to dark mode');
        toggleBtn.setAttribute('aria-pressed', 'false');
    }
}

function getThemeColors(isDark) {
    return {
        axisLine: isDark ? '#30363d' : '#d0d7de',
        axisText: isDark ? '#8b949e' : '#656d76',
        splitLine: isDark ? '#21262d' : '#f0f0f4',
        tooltipBg: isDark ? '#161b22' : '#ffffff',
        tooltipBorder: isDark ? '#30363d' : '#e1e4e8',
        tooltipText: isDark ? '#e6edf3' : '#1f2328'
    };
}

function buildChartOption(key, config, dates, seriesData, isDark) {
    const colors = getThemeColors(isDark);
    const isRate = key.includes('rate');
    const isIndex = key.includes('index');
    const isWage = key.includes('wage');
    
    // Theme line colors: red for rates, green for indices, purple for wages, blue for commodity prices
    let lineColor = '#1e88e5';
    let gradientRgb = '30, 136, 229';
    if (isRate) {
        lineColor = '#e53935';
        gradientRgb = '229, 57, 53';
    } else if (isIndex) {
        lineColor = '#43a047';
        gradientRgb = '67, 160, 71';
    } else if (isWage) {
        lineColor = '#8e24aa';
        gradientRgb = '142, 36, 170';
    }

    return {
        tooltip: { 
            trigger: 'axis',
            backgroundColor: colors.tooltipBg,
            borderColor: colors.tooltipBorder,
            textStyle: { color: colors.tooltipText },
            valueFormatter: config.tooltipFormatter
        },
        grid: { 
            left: '3%', 
            right: '4%', 
            bottom: '3%', 
            top: '12%', 
            containLabel: true 
        },
        xAxis: {
            type: 'category',
            data: dates,
            boundaryGap: false,
            axisLine: { lineStyle: { color: colors.axisLine } },
            axisLabel: { color: colors.axisText }
        },
        yAxis: {
            type: 'value',
            name: config.unit,
            nameTextStyle: { color: colors.axisText },
            scale: true,
            axisLabel: {
                color: colors.axisText,
                formatter: config.axisFormatter
            },
            splitLine: {
                lineStyle: { color: colors.splitLine }
            }
        },
        series: [
            {
                name: config.title,
                type: 'line',
                data: seriesData,
                smooth: !isRate,
                step: isRate ? 'end' : false,
                itemStyle: { color: lineColor },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: `rgba(${gradientRgb}, 0.2)` },
                        { offset: 1, color: `rgba(${gradientRgb}, 0)` }
                    ])
                }
            }
        ]
    };
}

// ==========================================
// Dashboard Initialization
// ==========================================
const chartRegistry = [];

function applyTheme(theme, savePreference = true) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateToggleUI(currentTheme);

    if (savePreference) {
        storedTheme = currentTheme;
        try {
            localStorage.setItem('theme', currentTheme);
        } catch (error) {
            console.warn('Unable to save the theme preference:', error);
        }
    }

    const isDark = currentTheme === 'dark';
    chartRegistry.forEach(item => {
        item.chart.setOption(buildChartOption(item.key, item.config, item.dates, item.seriesData, isDark));
    });
}

updateToggleUI(currentTheme);
const toggleBtn = document.getElementById('theme-toggle');
if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
        applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
    });
}

if (prefersDarkTheme) {
    prefersDarkTheme.addEventListener('change', event => {
        if (!storedTheme) {
            applyTheme(event.matches ? 'dark' : 'light', false);
        }
    });
}

fetch('data/prices.json')
    .then(response => response.json())
    .then(data => {
        const dashboard = document.getElementById('dashboard');
        const dates = data.dates;
        const sections = {
            expenses: {
                title: 'Expenses & Cost of Living',
                description: 'Prices, housing costs, and interest rates that affect everyday expenses.',
                element: document.createElement('section'),
                grid: document.createElement('div')
            },
            income: {
                title: 'Income',
                description: 'Hourly wage measures that provide context for income over time.',
                element: document.createElement('section'),
                grid: document.createElement('div')
            }
        };

        updateToggleUI(currentTheme);

        Object.values(sections).forEach(section => {
            section.element.className = 'metric-section';
            const heading = document.createElement('h2');
            heading.className = 'metric-section-heading';
            heading.textContent = section.title;
            section.element.appendChild(heading);

            const description = document.createElement('p');
            description.className = 'metric-section-description';
            description.textContent = section.description;
            section.element.appendChild(description);

            section.grid.className = 'metric-grid';
            section.element.appendChild(section.grid);
            dashboard.appendChild(section.element);
        });

        Object.keys(data).forEach(key => {
            if (key === 'dates') return; 
            const section = key === 'average_hourly_wage' || key === 'median_hourly_wage'
                ? sections.income
                : sections.expenses;

            const config = METRIC_CONFIG[key] || {
                title: formatTitle(key),
                unit: '',
                description: '',
                axisFormatter: (v) => v,
                tooltipFormatter: (v) => v
            };

            const card = document.createElement('div');
            card.className = 'chart-card';
            
            const title = document.createElement('h3');
            title.className = 'chart-title';
            title.textContent = config.title;
            card.appendChild(title);

            if (config.description) {
                const desc = document.createElement('p');
                desc.className = 'chart-description';
                desc.textContent = config.description;
                card.appendChild(desc);
            }

            const chartDiv = document.createElement('div');
            chartDiv.className = 'chart-container';
            card.appendChild(chartDiv);
            
            section.grid.appendChild(card);

            const chart = echarts.init(chartDiv);
            const isDark = currentTheme === 'dark';
            chart.setOption(buildChartOption(key, config, dates, data[key], isDark));

            chartRegistry.push({
                chart,
                key,
                config,
                dates,
                seriesData: data[key]
            });
        });

        // Window resize + Dashboard ResizeObserver
        window.addEventListener('resize', () => {
            chartRegistry.forEach(item => item.chart.resize());
        });

        if (window.ResizeObserver) {
            const resizeObserver = new ResizeObserver(() => {
                chartRegistry.forEach(item => item.chart.resize());
            });
            resizeObserver.observe(dashboard);
        }
    })
    .catch(error => {
        console.error('Error loading data:', error);
        document.getElementById('dashboard').innerHTML = '<p style="color:red; padding: 20px;">Error loading data. Check the console.</p>';
    });
