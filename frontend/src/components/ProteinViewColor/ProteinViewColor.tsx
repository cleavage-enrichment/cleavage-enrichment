import { JSX } from "react";
import { styled } from "styled-components";
import { ProteinViewColorProps } from "./ProteinViewColor.props";

const Table = styled.table`
  border-collapse: collapse;
`;

const Cell = styled.td`
  padding: 0;
  height: 10px;
`;

const PeptideBar = styled.div`
  height: 1px;
  width: 100%;
  background-color: green;
`;

const aminoAcidColors: { [aa: string]: string } = {
  A: "bg-red-200",
  C: "bg-yellow-200",
  D: "bg-blue-200",
  E: "bg-blue-300",
  F: "bg-pink-200",
  G: "bg-green-200",
  H: "bg-purple-200",
  I: "bg-orange-200",
  K: "bg-indigo-200",
  L: "bg-orange-300",
  M: "bg-yellow-300",
  N: "bg-cyan-200",
  P: "bg-red-300",
  Q: "bg-cyan-300",
  R: "bg-indigo-300",
  S: "bg-green-300",
  T: "bg-lime-200",
  V: "bg-amber-200",
  W: "bg-pink-300",
  Y: "bg-purple-300",
  // fallback color if unknown
  X: "bg-gray-200",
};

export const ProteinViewColor: React.FC<ProteinViewColorProps> = ({
  protein,
  peptides,
}) => {
  const proteinLength = protein.length;

  return (
    <div className="overflow-auto">
      <Table className="table-fixed border-collapse">
        <tbody>
          {/* Protein sequence row */}
          <tr>
            {protein.split("").map((aa, index) => (
              <Cell
                key={index}
                className={aminoAcidColors[aa] || aminoAcidColors["X"]}
              >
                {aa}
              </Cell>
            ))}
          </tr>

          {/* Peptide rows */}
          {peptides.map((peptide, rowIndex) => {
            const cells: JSX.Element[] = [];

            // Empty cells before the peptide starts
            for (let i = 0; i < peptide.start - 1; i++) {
              cells.push(<Cell key={`empty-${i}`} />);
            }

            // Cells for the peptide sequence
            for (let j = 0; j < peptide.sequence.length; j++) {
              cells.push(
                <Cell
                  key={`peptide-${j}`}
                  className={
                    aminoAcidColors[peptide.sequence[j]] || aminoAcidColors["X"]
                  }
                >
                  {peptide.sequence[j]}
                </Cell>,
              );
            }

            // Fill remaining cells to maintain full row length
            const remaining =
              proteinLength - (peptide.start - 1 + peptide.sequence.length);
            for (let k = 0; k < remaining; k++) {
              cells.push(<Cell key={`filler-${k}`} />);
            }

            return <tr key={rowIndex}>{cells}</tr>;
          })}
        </tbody>
      </Table>
    </div>
  );
};
