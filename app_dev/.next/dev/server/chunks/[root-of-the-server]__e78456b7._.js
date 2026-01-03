module.exports = [
"[externals]/next/dist/compiled/next-server/app-route-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-route-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/@opentelemetry/api [external] (next/dist/compiled/@opentelemetry/api, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/@opentelemetry/api", () => require("next/dist/compiled/@opentelemetry/api"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/after-task-async-storage.external.js [external] (next/dist/server/app-render/after-task-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/after-task-async-storage.external.js", () => require("next/dist/server/app-render/after-task-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/path [external] (path, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("path", () => require("path"));

module.exports = mod;
}),
"[project]/src/app/api/dashboard/chart-data/route.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "GET",
    ()=>GET
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/server.js [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$externals$5d2f$better$2d$sqlite3__$5b$external$5d$__$28$better$2d$sqlite3$2c$__cjs$2c$__$5b$project$5d2f$node_modules$2f$better$2d$sqlite3$29$__ = __turbopack_context__.i("[externals]/better-sqlite3 [external] (better-sqlite3, cjs, [project]/node_modules/better-sqlite3)");
var __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/path [external] (path, cjs)");
;
;
;
async function GET(req) {
    try {
        const { searchParams } = new URL(req.url);
        const year = searchParams.get('year') || '2025';
        const month = searchParams.get('month') || 'all';
        const dbPath = __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(process.cwd(), 'financas_dev.db');
        const db = new __TURBOPACK__imported__module__$5b$externals$5d2f$better$2d$sqlite3__$5b$external$5d$__$28$better$2d$sqlite3$2c$__cjs$2c$__$5b$project$5d2f$node_modules$2f$better$2d$sqlite3$29$__["default"](dbPath);
        let whereClause = '';
        if (month !== 'all') {
            // Se um mês específico for selecionado, mostrar últimos 6 meses incluindo esse
            const selectedMonth = `${year}${month.padStart(2, '0')}`;
            whereClause = `WHERE MesFatura <= '${selectedMonth}' AND MesFatura > '${(parseInt(year) - 1).toString()}${month.padStart(2, '0')}'`;
        } else {
            // Se "todos os meses", mostrar todos os meses do ano
            whereClause = `WHERE MesFatura LIKE '${year}%'`;
        }
        // Buscar dados dos últimos meses
        const chartData = db.prepare(`
      SELECT 
        MesFatura,
        TipoTransacao,
        SUM(ValorPositivo) as valor
      FROM journal_entries
      ${whereClause} 
        AND MesFatura IS NOT NULL
        AND IgnorarDashboard = 0
      GROUP BY MesFatura, TipoTransacao
      ORDER BY MesFatura
    `).all();
        // Transformar dados para o formato do gráfico
        const chartMap = new Map();
        chartData.forEach((item)=>{
            const mes = item.MesFatura;
            if (!chartMap.has(mes)) {
                // Formatar mês (AAAAMM -> MMM/AAAA)
                const year = mes.substring(0, 4);
                const month = mes.substring(4, 6);
                const monthNames = [
                    'Jan',
                    'Fev',
                    'Mar',
                    'Abr',
                    'Mai',
                    'Jun',
                    'Jul',
                    'Ago',
                    'Set',
                    'Out',
                    'Nov',
                    'Dez'
                ];
                const mesFormatado = `${monthNames[parseInt(month) - 1]}/${year}`;
                chartMap.set(mes, {
                    receitas: 0,
                    despesas: 0,
                    mesFormatado
                });
            }
            const data = chartMap.get(mes);
            if (item.TipoTransacao === 'Receitas') {
                data.receitas = item.valor;
            } else if ([
                'Despesas',
                'Cartão de Crédito'
            ].includes(item.TipoTransacao)) {
                data.despesas += item.valor;
            }
        });
        // Converter para array e ordenar
        const chartArray = Array.from(chartMap.entries()).map(([mes, data])=>({
                mes: data.mesFormatado,
                receitas: data.receitas,
                despesas: data.despesas
            })).sort((a, b)=>{
            // Extrair ano e mês para ordenação
            const [mesA, anoA] = a.mes.split('/');
            const [mesB, anoB] = b.mes.split('/');
            const monthNames = [
                'Jan',
                'Fev',
                'Mar',
                'Abr',
                'Mai',
                'Jun',
                'Jul',
                'Ago',
                'Set',
                'Out',
                'Nov',
                'Dez'
            ];
            const mesNumA = monthNames.indexOf(mesA) + 1;
            const mesNumB = monthNames.indexOf(mesB) + 1;
            if (anoA !== anoB) return anoA.localeCompare(anoB);
            return mesNumA - mesNumB;
        });
        db.close();
        return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json(chartArray);
    } catch (error) {
        console.error('Error fetching chart data:', error);
        return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
            error: 'Internal server error'
        }, {
            status: 500
        });
    }
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__e78456b7._.js.map