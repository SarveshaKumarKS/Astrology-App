import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface ChartProps {
  houses: { [key: number]: string[] };
  title: string;
}

const SouthIndianChart: React.FC<ChartProps> = ({ houses, title }) => {
  const renderCell = (sign: number, isCenter: boolean = false) => {
    if (isCenter) {
      return (
        <View style={[styles.cell, styles.centerCell]}>
          <Text style={styles.centerText}>{title}</Text>
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
      <View style={styles.cell}>
        <Text style={styles.signNumber}>{sign}</Text>
        <Text style={styles.planetStack}>
          {planetLabels.join('\n')}
        </Text>
        {ascLabel && (
          <Text style={styles.lagna}>{ascLabel}</Text>
        )}
      </View>
    );
  };

  return (
    <View style={styles.chart}>
      {/* Row 1 - Shifted clockwise */}
      <View style={styles.row}>
        {renderCell(12)}
        {renderCell(1)}
        {renderCell(2)}
        {renderCell(3)}
      </View>
      
      {/* Row 2 - Shifted clockwise */}
      <View style={styles.row}>
        {renderCell(11)}
        {renderCell(0, true)}
        {renderCell(4)}
      </View>
      
      {/* Row 3 - Shifted clockwise */}
      <View style={styles.row}>
        {renderCell(10)}
        <View style={styles.centerSpacer} />
        {renderCell(5)}
      </View>
      
      {/* Row 4 - Shifted clockwise */}
      <View style={styles.row}>
        {renderCell(9)}
        {renderCell(8)}
        {renderCell(7)}
        {renderCell(6)}
      </View>
    </View>
  );
};

const CHART_SIZE = 360;
const BORDER = 2;
const CELL_BORDER = 1;
const CELL_SIZE = (CHART_SIZE - BORDER * 2 - CELL_BORDER * 3) / 4;

const styles = StyleSheet.create({
  chart: {
    width: CHART_SIZE,
    height: CHART_SIZE,
    backgroundColor: '#FFFBEA',
    borderWidth: BORDER,
    borderColor: '#333',
  },
  row: {
    flexDirection: 'row',
    height: CELL_SIZE,
  },
  cell: {
    width: CELL_SIZE,
    height: CELL_SIZE,
    borderWidth: CELL_BORDER,
    borderColor: '#333',
    padding: 6,
    backgroundColor: '#FFFBEA',
  },
  centerCell: {
    width: CELL_SIZE * 2 + CELL_BORDER * 2,
    height: CELL_SIZE * 2 + CELL_BORDER * 2,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 0,
  },
  centerSpacer: {
    width: CELL_SIZE * 2 + CELL_BORDER * 2,
    height: CELL_SIZE,
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
