import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface ChartProps {
  houses: { [key: number]: string[] };
  title: string;
  size?: number;
}

const SouthIndianChart: React.FC<ChartProps> = ({ houses, title, size = 320 }) => {
  const border = 2;
  const cellBorder = 1;
  const cellSize = (size - border * 2 - cellBorder * 3) / 4;

  const renderCell = (sign: number, isCenter: boolean = false) => {
    if (isCenter) {
      return (
        <View
          testID="south-indian-chart-center"
          style={[
            styles.cell,
            styles.centerCell,
            { width: cellSize * 2 + cellBorder * 2, height: cellSize * 2 + cellBorder * 2 },
          ]}
        >
          <Text style={[styles.centerText, { fontSize: Math.max(12, size * 0.044) }]}>{title}</Text>
        </View>
      );
    }

    const labels = houses[sign] || [];
    
    // Find Ascendant/Lagna
    const ascIdx = labels.findIndex(x => 
      ["Asc", "Lagna", "லக்"].includes(x)
    );
    
    let ascLabel = null;
    let planetLabels = [...labels];
    
    if (ascIdx >= 0) {
      ascLabel = labels[ascIdx];
      planetLabels.splice(ascIdx, 1);
    }

    return (
      <View testID={`south-indian-chart-house-${sign}`} style={[styles.cell, { width: cellSize, height: cellSize }]}>
        <Text style={styles.signNumber}>{sign}</Text>
        <Text style={[styles.planetStack, { fontSize: Math.max(9, size * 0.032), lineHeight: Math.max(12, size * 0.043) }]} numberOfLines={4}>
          {planetLabels.join('\n')}
        </Text>
        {ascLabel && (
          <Text style={styles.lagna}>{ascLabel}</Text>
        )}
      </View>
    );
  };

  return (
    <View testID="south-indian-chart" style={[styles.chart, { width: size, height: size }]}>
      {/* Row 1 - Shifted clockwise */}
      <View style={[styles.row, { height: cellSize }]}>
        {renderCell(12)}
        {renderCell(1)}
        {renderCell(2)}
        {renderCell(3)}
      </View>
      
      {/* Row 2 - Shifted clockwise */}
      <View style={[styles.row, { height: cellSize }]}>
        {renderCell(11)}
        {renderCell(0, true)}
        {renderCell(4)}
      </View>
      
      {/* Row 3 - Shifted clockwise */}
      <View style={[styles.row, { height: cellSize }]}>
        {renderCell(10)}
        <View style={[styles.centerSpacer, { width: cellSize * 2 + cellBorder * 2, height: cellSize }]} />
        {renderCell(5)}
      </View>
      
      {/* Row 4 - Shifted clockwise */}
      <View style={[styles.row, { height: cellSize }]}>
        {renderCell(9)}
        {renderCell(8)}
        {renderCell(7)}
        {renderCell(6)}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  chart: {
    backgroundColor: '#FFFBEA',
    borderWidth: 2,
    borderColor: '#333',
  },
  row: {
    flexDirection: 'row',
  },
  cell: {
    borderWidth: 1,
    borderColor: '#333',
    padding: 6,
    backgroundColor: '#FFFBEA',
  },
  centerCell: {
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 0,
  },
  centerSpacer: {
    borderWidth: 0,
  },
  centerText: {
    fontWeight: '700',
    fontSize: 16,
    textAlign: 'center',
    color: '#333',
  },
  signNumber: {
    position: 'absolute',
    right: 6,
    top: 4,
    opacity: 0.55,
    fontSize: 10,
    color: '#333',
  },
  lagna: {
    position: 'absolute',
    right: 6,
    bottom: 6,
    transform: [{ rotate: '-30deg' }],
    fontSize: 10,
    fontStyle: 'italic',
    color: '#333',
  },
  planetStack: {
    fontSize: 12,
    lineHeight: 16,
    color: '#333',
  },
});

export default SouthIndianChart;
