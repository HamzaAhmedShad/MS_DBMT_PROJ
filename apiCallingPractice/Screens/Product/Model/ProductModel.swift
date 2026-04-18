//
//  ProductModel.swift
//  apiCallingPractice
//
//  Created by BS1101 on 15/5/23.
//

import Foundation
struct ProductModel: Decodable {
    let id: Int
    let title: String
    let price: Float
    let description: String
    let category: String
    let image: String
    let rating: Rate
}
struct Rate: Decodable {
    let rate: Double
    let count: Int
}
